from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.auditoria import Auditoria
from app.models.item import Item
from app.models.movimentacao import Movimentacao
from app.models.usuario import Usuario
from app.routers import auth as auth_router

SENHA_NOVA = "uma-senha-longa-123"


@pytest.fixture(autouse=True)
def limpar_limite_de_tentativas():
    auth_router._falhas.clear()
    yield
    auth_router._falhas.clear()


def _criar(db, senha_hash, perfil="operador", ativo=True) -> Usuario:
    u = Usuario(
        nome="Fulano",
        email=f"u-{uuid4().hex}@example.org",
        senha_hash=senha_hash,
        perfil=perfil,
        ativo=ativo,
    )
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def admin(db, senha_hash_teste) -> Usuario:
    return _criar(db, senha_hash_teste, perfil="admin")


@pytest.fixture
def client_admin(client, admin, senha_teste) -> TestClient:
    r = client.post("/auth/login", json={"email": admin.email, "senha": senha_teste})
    assert r.status_code == 200
    return client


def _payload(**extra):
    base = {
        "nome": "Pessoa Nova",
        "email": f"novo-{uuid4().hex}@example.org",
        "senha": SENHA_NOVA,
        "perfil": "operador",
    }
    return {**base, **extra}


def test_sem_login_nao_acessa(client):
    assert client.get("/usuarios").status_code == 401
    assert client.post("/usuarios", json=_payload()).status_code == 401
    assert client.delete("/usuarios/1").status_code == 401


def test_operador_nao_cadastra_nem_lista(client_autenticado):
    assert client_autenticado.post("/usuarios", json=_payload()).status_code == 403
    assert client_autenticado.get("/usuarios").status_code == 403
    assert client_autenticado.delete("/usuarios/1").status_code == 403


def test_admin_cadastra_e_o_novo_usuario_consegue_entrar(client_admin, db):
    dados = _payload()
    r = client_admin.post("/usuarios", json={**dados, "email": dados["email"].upper()})
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["email"] == dados["email"]  # normalizado para minúsculas
    assert corpo["perfil"] == "operador"
    assert corpo["ativo"] is True
    assert "senha" not in corpo and "senha_hash" not in corpo

    guardado = db.get(Usuario, corpo["id"])
    assert guardado.senha_hash.startswith("$argon2id$")

    client_admin.post("/auth/logout")
    r = client_admin.post(
        "/auth/login", json={"email": dados["email"], "senha": SENHA_NOVA}
    )
    assert r.status_code == 200


def test_cadastro_gera_auditoria(client_admin, admin, db):
    r = client_admin.post("/usuarios", json=_payload())
    linha = db.scalars(
        select(Auditoria).where(Auditoria.acao == "usuario_criado")
    ).one()
    assert linha.usuario_id == admin.id
    assert f"id={r.json()['id']}" in linha.detalhe
    assert SENHA_NOVA not in (linha.detalhe or "")


def test_email_duplicado_da_409(client_admin, admin):
    r = client_admin.post("/usuarios", json=_payload(email=admin.email))
    assert r.status_code == 409


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("senha", "curta"),
        ("email", "isto-nao-e-email"),
        ("nome", " "),
        ("perfil", "superusuario"),
    ],
)
def test_dados_invalidos_dao_422(client_admin, campo, valor):
    assert client_admin.post("/usuarios", json=_payload(**{campo: valor})).status_code == 422


def test_listar_nao_expoe_senha(client_admin, admin):
    r = client_admin.get("/usuarios")
    assert r.status_code == 200
    assert any(u["id"] == admin.id for u in r.json())
    assert all("senha_hash" not in u and "senha" not in u for u in r.json())


def test_admin_nao_desativa_nem_rebaixa_a_si_mesmo(client_admin, admin):
    assert client_admin.patch(f"/usuarios/{admin.id}", json={"ativo": False}).status_code == 400
    assert client_admin.patch(f"/usuarios/{admin.id}", json={"perfil": "operador"}).status_code == 400


def test_admin_nao_exclui_a_si_mesmo(client_admin, admin, db):
    r = client_admin.delete(f"/usuarios/{admin.id}")
    assert r.status_code == 400
    assert db.get(Usuario, admin.id) is not None


def test_nao_exclui_ultimo_administrador_ativo(client_admin, admin, db):
    r = client_admin.delete(f"/usuarios/{admin.id + 100000}")
    assert r.status_code == 404
    r = client_admin.delete(f"/usuarios/{admin.id}")
    assert r.status_code == 400
    assert db.get(Usuario, admin.id) is not None


def test_nao_desativa_ultimo_administrador_ativo(client_admin, admin, db):
    r = client_admin.patch(f"/usuarios/{admin.id}", json={"ativo": False})
    assert r.status_code == 400
    assert db.get(Usuario, admin.id).ativo is True


def test_exclui_admin_inativo_quando_outro_ativo(client_admin, admin, db, senha_hash_teste):
    outro_admin = _criar(db, senha_hash_teste, perfil="admin", ativo=False)
    r = client_admin.delete(f"/usuarios/{admin.id + 100000}")
    assert r.status_code == 404
    # Um administrador inativo não conta como administrador ativo.
    r = client_admin.delete(f"/usuarios/{outro_admin.id}")
    assert r.status_code == 204
    assert db.get(Usuario, outro_admin.id) is None
    assert db.get(Usuario, admin.id) is not None


def test_excluir_admin_quando_existe_outro_ativo(client_admin, db, senha_hash_teste):
    outro_admin = _criar(db, senha_hash_teste, perfil="admin")
    r = client_admin.delete(f"/usuarios/{outro_admin.id}")
    assert r.status_code == 204
    assert db.get(Usuario, outro_admin.id) is None


def test_excluir_usuario_preserva_auditoria_itens_e_movimentacoes(
    client_admin, admin, db, senha_hash_teste
):
    alvo = _criar(db, senha_hash_teste)
    item = Item(
        nome=f"Item histórico {uuid4().hex[:8]}",
        unidade="un",
        criado_por=alvo.id,
    )
    db.add(item)
    db.flush()

    movimento = Movimentacao(
        item_id=item.id,
        tipo="entrada",
        quantidade=Decimal("3.00"),
        usuario_id=alvo.id,
    )
    auditoria_antiga = Auditoria(
        usuario_id=alvo.id,
        acao="acao_anterior",
        detalhe="registro anterior à exclusão",
    )
    db.add_all([movimento, auditoria_antiga])
    db.commit()

    alvo_id, item_id, movimento_id, auditoria_id = (
        alvo.id, item.id, movimento.id, auditoria_antiga.id
    )
    r = client_admin.delete(f"/usuarios/{alvo_id}")

    assert r.status_code == 204
    assert db.get(Usuario, alvo_id) is None

    item_guardado = db.get(Item, item_id)
    movimento_guardado = db.get(Movimentacao, movimento_id)
    auditoria_guardada = db.get(Auditoria, auditoria_id)
    assert item_guardado is not None and item_guardado.criado_por == alvo_id
    assert movimento_guardado is not None and movimento_guardado.usuario_id == alvo_id
    assert auditoria_guardada is not None and auditoria_guardada.usuario_id == alvo_id

    evento = db.scalars(
        select(Auditoria).where(
            Auditoria.acao == "usuario_excluido",
            Auditoria.usuario_id == admin.id,
        )
    ).one()
    assert f"id={alvo_id}" in evento.detalhe


def test_excluir_usuario_inexistente_da_404(client_admin):
    assert client_admin.delete("/usuarios/999999").status_code == 404


def test_atualizar_usuario_inexistente_da_404(client_admin):
    assert client_admin.patch("/usuarios/999999", json={"ativo": False}).status_code == 404


def test_desativar_derruba_a_sessao_na_hora(client_admin, db, senha_hash_teste, senha_teste):
    operador = _criar(db, senha_hash_teste)
    outro = TestClient(app, base_url="https://testserver")  # outro navegador
    assert outro.post(
        "/auth/login", json={"email": operador.email, "senha": senha_teste}
    ).status_code == 200
    assert outro.get("/auth/eu").status_code == 200

    r = client_admin.patch(f"/usuarios/{operador.id}", json={"ativo": False})
    assert r.status_code == 200 and r.json()["ativo"] is False

    assert outro.get("/auth/eu").status_code == 401
    assert outro.post(
        "/auth/login", json={"email": operador.email, "senha": senha_teste}
    ).status_code == 401


def test_promover_e_reativar(client_admin, db, senha_hash_teste):
    u = _criar(db, senha_hash_teste, ativo=False)
    r = client_admin.patch(f"/usuarios/{u.id}", json={"ativo": True, "perfil": "admin"})
    assert r.status_code == 200
    assert r.json()["ativo"] is True and r.json()["perfil"] == "admin"


def test_admin_redefine_senha_de_outro_usuario(client_admin, db, senha_hash_teste, senha_teste):
    u = _criar(db, senha_hash_teste)
    r = client_admin.post(f"/usuarios/{u.id}/senha", json={"senha_nova": SENHA_NOVA})
    assert r.status_code == 204
    client_admin.post("/auth/logout")
    assert client_admin.post(
        "/auth/login", json={"email": u.email, "senha": senha_teste}
    ).status_code == 401
    assert client_admin.post(
        "/auth/login", json={"email": u.email, "senha": SENHA_NOVA}
    ).status_code == 200


def test_operador_nao_redefine_senha(client_autenticado, db, senha_hash_teste):
    alvo = _criar(db, senha_hash_teste)
    r = client_autenticado.post(f"/usuarios/{alvo.id}/senha", json={"senha_nova": SENHA_NOVA})
    assert r.status_code == 403
