from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.item import Item
from app.models.movimentacao import Movimentacao
from app.models.usuario import Usuario


def criar_item(client: TestClient) -> int:
    response = client.post("/itens", json={"nome": "Feijão", "unidade": "kg"})
    assert response.status_code == 201
    return response.json()["id"]


def test_operador_nao_pode_limpar_historico(
    client_autenticado: TestClient, db: Session
):
    item_id = criar_item(client_autenticado)
    assert client_autenticado.post(
        "/movimentacoes",
        json={"item_id": item_id, "tipo": "entrada", "quantidade": "8.00"},
    ).status_code == 201

    response = client_autenticado.delete("/movimentacoes/historico")

    assert response.status_code == 403
    assert db.scalar(select(func.count()).select_from(Movimentacao)) == 1
    assert db.get(Item, item_id).saldo == Decimal("8.00")


def test_administrador_limpa_historico_sem_alterar_saldos(
    client_autenticado: TestClient, db: Session, usuario: Usuario
):
    usuario.perfil = "admin"
    db.commit()
    item_id = criar_item(client_autenticado)
    assert client_autenticado.post(
        "/movimentacoes",
        json={"item_id": item_id, "tipo": "entrada", "quantidade": "8.00"},
    ).status_code == 201
    assert client_autenticado.post(
        "/movimentacoes",
        json={"item_id": item_id, "tipo": "saida", "quantidade": "3.00"},
    ).status_code == 201

    response = client_autenticado.delete("/movimentacoes/historico")

    assert response.status_code == 200
    assert response.json() == {"removidas": 2, "saldos_preservados": True}
    assert db.scalar(select(func.count()).select_from(Movimentacao)) == 0
    db.expire_all()
    assert db.get(Item, item_id).saldo == Decimal("5.00")
    auditoria = db.scalars(
        select(Auditoria).where(Auditoria.acao == "historico_movimentacoes_limpo")
    ).all()
    assert len(auditoria) == 1
    assert auditoria[0].usuario_id == usuario.id
    assert "registros_removidos=2" in auditoria[0].detalhe

    # A limpeza não pode desativar os próximos registros do histórico.
    novo = client_autenticado.post(
        "/movimentacoes",
        json={"item_id": item_id, "tipo": "entrada", "quantidade": "1.00"},
    )
    assert novo.status_code == 201
    historico = client_autenticado.get("/movimentacoes?limite=10")
    assert historico.status_code == 200
    assert len(historico.json()) == 1
    assert historico.json()[0]["id"] == novo.json()["id"]


def test_limpar_historico_sem_registros_e_seguro(
    client_autenticado: TestClient, db: Session, usuario: Usuario
):
    usuario.perfil = "admin"
    db.commit()

    response = client_autenticado.delete("/movimentacoes/historico")

    assert response.status_code == 200
    assert response.json() == {"removidas": 0, "saldos_preservados": True}
