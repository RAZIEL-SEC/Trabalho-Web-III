from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.main import app
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.routers import auth as auth_router


@pytest.fixture(autouse=True)
def limpar_limite_de_tentativas():
    auth_router._falhas.clear()
    yield
    auth_router._falhas.clear()


def _login(client, email, senha):
    return client.post("/auth/login", json={"email": email, "senha": senha})


def test_login_ok_define_cookie_seguro(client, usuario, senha_teste):
    r = _login(client, usuario.email, senha_teste)
    assert r.status_code == 200
    assert r.json()["email"] == usuario.email
    assert r.json()["perfil"] == "operador"
    assert "senha_hash" not in r.json()
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie


def test_erros_de_login_tem_a_mesma_resposta(client, usuario):
    senha_errada = _login(client, usuario.email, "senha-errada-123")
    email_inexistente = _login(client, "nao-existe@example.org", "senha-errada-123")
    assert senha_errada.status_code == email_inexistente.status_code == 401
    assert senha_errada.json() == email_inexistente.json()


def test_usuario_inativo_nao_entra(client, db, usuario, senha_teste):
    usuario.ativo = False
    db.commit()
    assert _login(client, usuario.email, senha_teste).status_code == 401


def test_eu_sem_login_e_401(client):
    assert client.get("/auth/eu").status_code == 401


def test_eu_com_login(client_autenticado, usuario):
    r = client_autenticado.get("/auth/eu")
    assert r.status_code == 200
    assert r.json()["email"] == usuario.email


def test_logout_encerra_a_sessao(client_autenticado):
    assert client_autenticado.post("/auth/logout").status_code == 204
    assert client_autenticado.get("/auth/eu").status_code == 401


def test_bloqueia_apos_5_senhas_erradas(client, usuario, senha_teste):
    for _ in range(5):
        assert _login(client, usuario.email, "senha-errada-123").status_code == 401
    # depois do limite, até a senha certa fica bloqueada por um tempo
    assert _login(client, usuario.email, senha_teste).status_code == 429


def test_login_gera_auditoria(client, db, usuario, senha_teste):
    _login(client, usuario.email, "senha-errada-123")
    _login(client, usuario.email, senha_teste)
    acoes = list(db.scalars(select(Auditoria.acao).order_by(Auditoria.id)))
    assert acoes == ["login_falha", "login_ok"]


def test_auditoria_nao_grava_o_email_digitado_de_quem_nao_existe(client, db):
    _login(client, "alguem-digitou-a-senha-aqui", "x" * 12)
    linha = db.scalars(select(Auditoria)).one()
    assert linha.acao == "login_falha"
    assert linha.usuario_id is None
    assert linha.detalhe is None


def test_auditoria_e_imutavel(db, usuario):
    db.add(Auditoria(usuario_id=usuario.id, acao="teste"))
    db.commit()
    with pytest.raises(DBAPIError):
        db.execute(text("UPDATE auditoria SET acao = 'adulterado'"))


def test_trocar_senha(client_autenticado, usuario, senha_teste):
    nova = "uma-senha-nova-bem-longa"
    r = client_autenticado.post(
        "/auth/trocar-senha", json={"senha_atual": senha_teste, "senha_nova": nova}
    )
    assert r.status_code == 204
    client_autenticado.post("/auth/logout")
    assert _login(client_autenticado, usuario.email, senha_teste).status_code == 401
    assert _login(client_autenticado, usuario.email, nova).status_code == 200


def test_trocar_senha_exige_a_atual_correta(client_autenticado):
    r = client_autenticado.post(
        "/auth/trocar-senha",
        json={"senha_atual": "errada-errada", "senha_nova": "uma-senha-nova-bem-longa"},
    )
    assert r.status_code == 400


def test_trocar_senha_recusa_senha_curta(client_autenticado, senha_teste):
    r = client_autenticado.post(
        "/auth/trocar-senha", json={"senha_atual": senha_teste, "senha_nova": "curta"}
    )
    assert r.status_code == 422


def test_senha_fica_em_argon2id(db, usuario):
    assert db.get(Usuario, usuario.id).senha_hash.startswith("$argon2id$")
