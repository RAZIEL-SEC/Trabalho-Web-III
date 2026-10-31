from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from decimal import Decimal
from pathlib import Path
from time import monotonic, sleep
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, insert, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.core.deps import get_db, get_usuario_atual
from app.db.session import engine
from app.main import app
from app.models.item import Item
from app.models.movimentacao import Movimentacao
from app.models.usuario import Usuario


@pytest.fixture
def clientes_concorrentes(
    senha_hash_teste: str, senha_teste: str,
) -> Iterator[tuple[list[TestClient], str, str]]:
    """Conexões independentes precisam enxergar um schema já confirmado."""
    assert get_usuario_atual not in app.dependency_overrides
    schema = f"test_concorrencia_{uuid4().hex}"
    application_name = f"test_mov_{uuid4().hex}"
    schema_sql = (
        Path(__file__).resolve().parents[2] / "database" / "schema.sql"
    ).read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.execute(CreateSchema(schema))
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        connection.exec_driver_sql(schema_sql)
        connection.execute(insert(Usuario).values(
            nome="Usuário concorrência", email="concorrencia@example.org",
            senha_hash=senha_hash_teste, ativo=True,
        ))

    def configurar_transacao(session, transaction, connection):
        # Configura toda nova transação, inclusive após commit/refresh das
        # rotas, sem deixar search_path ou timeouts na conexão do pool.
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        connection.execute(
            text("SELECT set_config('application_name', :nome, true)"),
            {"nome": application_name},
        )
        connection.exec_driver_sql("SET LOCAL lock_timeout TO '15s'")
        connection.exec_driver_sql("SET LOCAL statement_timeout TO '20s'")

    def get_db_concorrente() -> Iterator[Session]:
        with Session(engine, autoflush=False) as db:
            event.listen(db, "after_begin", configurar_transacao)
            yield db

    overrides_anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = get_db_concorrente
    try:
        with ExitStack() as stack:
            clientes = [
                stack.enter_context(TestClient(app, base_url="https://testserver"))
                for _ in range(2)
            ]
            for client in clientes:
                login = client.post("/auth/login", json={
                    "email": "concorrencia@example.org", "senha": senha_teste,
                })
                assert login.status_code == 200
            yield clientes, schema, application_name
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides_anteriores)
        # Exclusão restrita ao schema aleatório criado por esta fixture.
        with engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        with engine.connect() as connection:
            assert connection.scalar(
                text("SELECT to_regnamespace(:schema)"), {"schema": schema}
            ) is None


@pytest.mark.parametrize(
    "saldo_inicial,operacoes,status_esperados,saldo_final",
    [
        pytest.param(
            "0.00", [("entrada", "2.35"), ("entrada", "3.15")],
            [201, 201], "5.50", id="entradas-sem-perder-atualizacao",
        ),
        pytest.param(
            "5.00", [("saida", "4.00"), ("saida", "4.00")],
            [201, 409], "1.00", id="saidas-nao-podem-consumir-o-mesmo-saldo",
        ),
        pytest.param(
            "10.00", [("saida", "4.00"), ("saida", "3.00")],
            [201, 201], "3.00", id="saidas-com-saldo-suficiente",
        ),
        pytest.param(
            "5.00", [("entrada", "2.00"), ("saida", "4.00")],
            [201, 201], "3.00", id="entrada-e-saida-simultaneas",
        ),
    ],
)
def test_movimentacoes_simultaneas_preservam_saldo_e_historico(
    clientes_concorrentes, saldo_inicial: str, operacoes: list,
    status_esperados: list[int], saldo_final: str,
):
    clientes, schema, application_name = clientes_concorrentes
    cadastro = clientes[0].post(
        "/itens", json={"nome": "Arroz concorrência", "unidade": "kg"}
    )
    assert cadastro.status_code == 201
    item_id = cadastro.json()["id"]
    if Decimal(saldo_inicial) > 0:
        entrada = clientes[0].post("/movimentacoes", json={
            "item_id": item_id, "tipo": "entrada", "quantidade": saldo_inicial,
        })
        assert entrada.status_code == 201

    with engine.connect() as bloqueio:
        transaction = bloqueio.begin()
        bloqueio.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        bloqueio.execute(
            select(Item.id).where(Item.id == item_id).with_for_update()
        ).one()

        with ThreadPoolExecutor(max_workers=2) as executor:
            tarefas = [
                executor.submit(client.post, "/movimentacoes", json={
                    "item_id": item_id, "tipo": tipo, "quantidade": quantidade,
                })
                for client, (tipo, quantidade) in zip(clientes, operacoes)
            ]
            try:
                # Aguarda evidência do PostgreSQL de que ambas chegaram ao
                # bloqueio. Não depende de sleeps para presumir concorrência.
                with engine.connect().execution_options(
                    isolation_level="AUTOCOMMIT"
                ) as monitor:
                    prazo = monotonic() + 5
                    while monotonic() < prazo:
                        aguardando = monitor.scalar(text("""
                            SELECT count(*) FROM pg_stat_activity
                            WHERE application_name = :nome
                              AND wait_event_type = 'Lock'
                        """), {"nome": application_name})
                        if aguardando == 2:
                            break
                        sleep(0.02)
                    assert aguardando == 2, "As duas requisições devem disputar o bloqueio"
            finally:
                transaction.rollback()

            respostas = [tarefa.result(timeout=20) for tarefa in tarefas]

    assert sorted(response.status_code for response in respostas) == status_esperados
    sucessos = [response for response in respostas if response.status_code == 201]
    assert any(response.json()["saldo_atual"] == saldo_final for response in sucessos)
    for response in respostas:
        if response.status_code == 409:
            assert response.json() == {"detail": "Saldo insuficiente para a saída."}

    with engine.begin() as connection:
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        saldo = connection.scalar(select(Item.saldo).where(Item.id == item_id))
        historico = connection.execute(
            select(Movimentacao.tipo, Movimentacao.quantidade)
            .where(Movimentacao.item_id == item_id)
        ).all()
    assert saldo == Decimal(saldo_final)
    assert saldo >= 0
    assert len(historico) == len(sucessos) + int(Decimal(saldo_inicial) > 0)
    assert sum(
        quantidade if tipo == "entrada" else -quantidade
        for tipo, quantidade in historico
    ) == saldo
    assert clientes[0].get("/itens").json()[0]["saldo"] == saldo_final


@pytest.mark.parametrize("tipo,saldo_final", [("entrada", "12.00"), ("saida", "8.00")])
def test_falha_no_commit_reverte_saldo_e_historico(
    clientes_concorrentes, tipo: str, saldo_final: str,
):
    clientes, schema, _ = clientes_concorrentes
    client = clientes[0]
    cadastro = client.post("/itens", json={"nome": "Arroz", "unidade": "kg"})
    assert cadastro.status_code == 201
    item_id = cadastro.json()["id"]
    assert client.post("/movimentacoes", json={
        "item_id": item_id, "tipo": "entrada", "quantidade": "10.00",
    }).status_code == 201

    with engine.begin() as connection:
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        # Diferentemente do trigger imediato, este só falha no COMMIT real.
        connection.exec_driver_sql("""
            CREATE FUNCTION falhar_commit_teste() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'Falha de commit simulada pelo teste';
            END;
            $$ LANGUAGE plpgsql;
            CREATE CONSTRAINT TRIGGER trg_falhar_commit_teste
                AFTER INSERT ON movimentacoes
                DEFERRABLE INITIALLY DEFERRED
                FOR EACH ROW EXECUTE FUNCTION falhar_commit_teste();
        """)

    with pytest.raises(DBAPIError):
        client.post("/movimentacoes", json={
            "item_id": item_id, "tipo": tipo, "quantidade": "2.00",
        })

    assert client.get("/itens").json()[0]["saldo"] == "10.00"
    with engine.begin() as connection:
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        historico = connection.execute(
            select(Movimentacao.tipo, Movimentacao.quantidade)
        ).all()
        assert historico == [("entrada", Decimal("10.00"))]
        connection.exec_driver_sql("DROP TRIGGER trg_falhar_commit_teste ON movimentacoes")

    response = client.post("/movimentacoes", json={
        "item_id": item_id, "tipo": tipo, "quantidade": "2.00",
    })
    assert response.status_code == 201
    assert response.json()["saldo_atual"] == saldo_final
