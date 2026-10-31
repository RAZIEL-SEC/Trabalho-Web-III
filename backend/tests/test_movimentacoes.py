from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.security import COOKIE_NOME
from app.models.item import Item
from app.models.movimentacao import Movimentacao
from app.models.usuario import Usuario


@pytest.fixture
def item_id(client_autenticado: TestClient) -> int:
    response = client_autenticado.post(
        "/itens", json={"nome": "Arroz", "unidade": "kg"}
    )
    assert response.status_code == 201
    return response.json()["id"]


def movimentar(
    client: TestClient, item_id: int, tipo: str, quantidade: str
):
    return client.post(
        "/movimentacoes",
        json={"item_id": item_id, "tipo": tipo, "quantidade": quantidade},
    )


def verificar_estado(db: Session, item_id: int, saldo: str, total: int) -> None:
    db.expire_all()
    assert db.get(Item, item_id).saldo == Decimal(saldo)
    assert db.scalar(
        select(func.count()).select_from(Movimentacao)
        .where(Movimentacao.item_id == item_id)
    ) == total


def test_movimentacao_sem_autenticacao_retorna_401(client: TestClient, db: Session):
    response = movimentar(client, 1, "entrada", "1.00")

    assert response.status_code == 401
    assert response.json() == {"detail": "Não autenticado"}
    assert db.scalar(select(func.count()).select_from(Movimentacao)) == 0


def test_cookie_invalido_retorna_401(client: TestClient):
    client.cookies.set(COOKIE_NOME, "cookie-invalido")

    assert movimentar(client, 1, "entrada", "1.00").status_code == 401


def test_usuario_inativo_nao_movimenta(
    client_autenticado: TestClient, db: Session, usuario: Usuario, item_id: int
):
    usuario.ativo = False
    db.commit()

    assert movimentar(
        client_autenticado, item_id, "entrada", "1.00"
    ).status_code == 401
    verificar_estado(db, item_id, "0.00", 0)


@pytest.mark.parametrize("quantidade", ["0.01", "2.35", "2.3500", 1, 1.25])
def test_entrada_persiste_historico_e_soma_saldo(
    client_autenticado: TestClient,
    db: Session,
    usuario: Usuario,
    item_id: int,
    quantidade,
):
    esperado = Decimal(str(quantidade)).quantize(Decimal("0.01"))
    response = client_autenticado.post(
        "/movimentacoes",
        json={
            "item_id": item_id, "tipo": "entrada", "quantidade": quantidade,
            "observacao": "  Doação recebida  ",
        },
    )

    assert response.status_code == 201
    dados = response.json()
    assert set(dados) == {
        "id", "item_id", "tipo", "quantidade", "observacao", "usuario_id",
        "criado_em", "saldo_atual",
    }
    assert dados["item_id"] == item_id
    assert dados["tipo"] == "entrada"
    assert dados["quantidade"] == str(esperado)
    assert dados["saldo_atual"] == str(esperado)
    assert dados["usuario_id"] == usuario.id
    assert dados["observacao"] == "Doação recebida"
    assert datetime.fromisoformat(dados["criado_em"]).tzinfo is not None

    verificar_estado(db, item_id, str(esperado), 1)
    movimentacao = db.get(Movimentacao, dados["id"])
    assert movimentacao.item_id == item_id
    assert movimentacao.tipo == "entrada"
    assert movimentacao.quantidade == esperado
    assert movimentacao.observacao == "Doação recebida"
    assert movimentacao.usuario_id == usuario.id
    assert movimentacao.estorno_de is None
    assert movimentacao.motivo is None
    assert movimentacao.criado_em == datetime.fromisoformat(dados["criado_em"])
    itens = client_autenticado.get("/itens").json()
    assert itens[0]["saldo"] == str(esperado)


@pytest.mark.parametrize("quantidade", ["0.01", "2.35", "10.50"])
def test_saida_subtrai_saldo_inclusive_ate_zero(
    client_autenticado: TestClient, db: Session, item_id: int, quantidade: str
):
    assert movimentar(
        client_autenticado, item_id, "entrada", "10.50"
    ).status_code == 201

    response = movimentar(client_autenticado, item_id, "saida", quantidade)

    assert response.status_code == 201
    saldo = Decimal("10.50") - Decimal(quantidade)
    assert response.json()["tipo"] == "saida"
    assert response.json()["quantidade"] == quantidade
    assert response.json()["saldo_atual"] == str(saldo)
    assert response.json()["observacao"] is None
    verificar_estado(db, item_id, str(saldo), 2)
    assert db.get(Movimentacao, response.json()["id"]).quantidade == Decimal(quantidade)


def test_operacoes_decimais_nao_perdem_precisao(
    client_autenticado: TestClient, db: Session, item_id: int
):
    for tipo, quantidade in (("entrada", "0.10"), ("entrada", "0.20"), ("saida", "0.10")):
        response = movimentar(client_autenticado, item_id, tipo, quantidade)
        assert response.status_code == 201

    assert response.json()["saldo_atual"] == "0.20"
    verificar_estado(db, item_id, "0.20", 3)


def test_saldo_insuficiente_reverte_e_permite_nova_movimentacao(
    client_autenticado: TestClient, db: Session, item_id: int
):
    assert movimentar(
        client_autenticado, item_id, "entrada", "2.00"
    ).status_code == 201

    response = movimentar(client_autenticado, item_id, "saida", "2.01")

    assert response.status_code == 409
    assert response.json() == {"detail": "Saldo insuficiente para a saída."}
    assert db.is_active
    verificar_estado(db, item_id, "2.00", 1)
    assert movimentar(
        client_autenticado, item_id, "saida", "2.00"
    ).status_code == 201
    verificar_estado(db, item_id, "0.00", 2)


def test_saida_com_saldo_zero_e_recusada(
    client_autenticado: TestClient, db: Session, item_id: int
):
    assert movimentar(
        client_autenticado, item_id, "saida", "0.01"
    ).status_code == 409
    verificar_estado(db, item_id, "0.00", 0)


def test_item_inexistente_retorna_404(client_autenticado: TestClient, db: Session):
    response = movimentar(client_autenticado, 2147483647, "entrada", "1.00")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item não encontrado."}
    assert db.is_active
    assert db.scalar(select(func.count()).select_from(Movimentacao)) == 0


@pytest.mark.parametrize("tipo", ["entrada", "saida"])
def test_item_inativo_nao_recebe_movimentacao(
    client_autenticado: TestClient, db: Session, item_id: int, tipo: str
):
    assert movimentar(
        client_autenticado, item_id, "entrada", "10.00"
    ).status_code == 201
    db.get(Item, item_id).ativo = False
    db.commit()

    response = movimentar(client_autenticado, item_id, tipo, "1.00")

    assert response.status_code == 409
    assert response.json() == {"detail": "Item inativo."}
    verificar_estado(db, item_id, "10.00", 1)


def test_saldo_maximo_nao_pode_ser_ultrapassado(
    client_autenticado: TestClient, db: Session, item_id: int
):
    assert movimentar(
        client_autenticado, item_id, "entrada", "99999999.99"
    ).status_code == 201

    response = movimentar(client_autenticado, item_id, "entrada", "0.01")

    assert response.status_code == 409
    assert response.json() == {"detail": "Saldo máximo do item excedido."}
    verificar_estado(db, item_id, "99999999.99", 1)


def test_autor_vem_do_usuario_do_cookie(
    client_autenticado: TestClient, db: Session, usuario: Usuario,
    senha_hash_teste: str, senha_teste: str, item_id: int,
):
    outro = Usuario(
        nome="Outro usuário", email="outro@example.org",
        senha_hash=senha_hash_teste, ativo=True,
    )
    db.add(outro)
    db.commit()
    outro_id = outro.id
    assert outro_id != usuario.id
    login = client_autenticado.post(
        "/auth/login", json={"email": outro.email, "senha": senha_teste}
    )
    assert login.status_code == 200

    response = movimentar(client_autenticado, item_id, "entrada", "1.00")

    assert response.status_code == 201
    assert response.json()["usuario_id"] == outro_id
    db.expire_all()
    assert db.get(Movimentacao, response.json()["id"]).usuario_id == outro_id
    assert db.get(Item, item_id).criado_por == usuario.id


@pytest.mark.parametrize(
    "alteracoes",
    [
        {"quantidade": 0}, {"quantidade": "-1"}, {"quantidade": "0.001"},
        {"quantidade": "100000000.00"}, {"quantidade": "NaN"},
        {"quantidade": "Infinity"}, {"quantidade": "-Infinity"},
        {"quantidade": "abc"}, {"quantidade": None}, {"quantidade": True},
        {"item_id": 0}, {"item_id": -1}, {"item_id": 2147483648},
        {"item_id": "1"}, {"item_id": 1.5}, {"item_id": True}, {"item_id": None},
        {"tipo": "estorno"}, {"tipo": "ENTRADA"}, {"tipo": "outro"}, {"tipo": None},
        {"observacao": "a" * 1001}, {"observacao": 123},
        {"usuario_id": 999}, {"saldo": "999.00"}, {"saldo_atual": "999.00"},
        {"estorno_de": 1}, {"motivo": "teste"}, {"id": 999},
        {"criado_em": "2026-01-01T00:00:00Z"},
    ],
)
def test_dados_invalidos_nao_alteram_saldo_ou_historico(
    client_autenticado: TestClient, db: Session, item_id: int, alteracoes: dict
):
    dados = {"item_id": item_id, "tipo": "entrada", "quantidade": "1.00"}
    dados.update(alteracoes)

    response = client_autenticado.post("/movimentacoes", json=dados)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    verificar_estado(db, item_id, "0.00", 0)


@pytest.mark.parametrize("campo", ["item_id", "tipo", "quantidade"])
def test_campo_obrigatorio_ausente_retorna_422(
    client_autenticado: TestClient, db: Session, item_id: int, campo: str
):
    dados = {"item_id": item_id, "tipo": "entrada", "quantidade": "1.00"}
    del dados[campo]

    assert client_autenticado.post("/movimentacoes", json=dados).status_code == 422
    verificar_estado(db, item_id, "0.00", 0)


@pytest.mark.parametrize("tipo,saldo_final", [("entrada", "12.00"), ("saida", "8.00")])
def test_falha_no_historico_reverte_tambem_o_saldo(
    client_autenticado: TestClient, db: Session, item_id: int,
    tipo: str, saldo_final: str,
):
    assert movimentar(
        client_autenticado, item_id, "entrada", "10.00"
    ).status_code == 201
    # Falha real no PostgreSQL, restrita ao schema de teste. Não simula commit
    # nem substitui a lógica da aplicação por mocks.
    db.execute(text("""
        CREATE FUNCTION falhar_movimentacao_teste() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'Falha de insercao simulada pelo teste';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_falhar_movimentacao_teste
            BEFORE INSERT ON movimentacoes
            FOR EACH ROW EXECUTE FUNCTION falhar_movimentacao_teste();
    """))
    db.commit()

    with pytest.raises(DBAPIError):
        movimentar(client_autenticado, item_id, tipo, "2.00")

    assert db.is_active
    verificar_estado(db, item_id, "10.00", 1)
    db.execute(text("DROP TRIGGER trg_falhar_movimentacao_teste ON movimentacoes"))
    db.commit()
    assert movimentar(
        client_autenticado, item_id, tipo, "2.00"
    ).status_code == 201
    verificar_estado(db, item_id, saldo_final, 2)
