"""Versão do token: sessões antigas caem quando a senha muda, o usuário é desativado etc."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select

from app.core.config import Settings, settings
from app.core.security import ALGORITMO, COOKIE_NOME, criar_token
from app.main import app
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.routers import auth as auth_router

NOVA_SENHA = "uma-senha-nova-bem-longa"


@pytest.fixture(autouse=True)
def limpar_limite_de_tentativas():
    auth_router._falhas.clear()
    yield
    auth_router._falhas.clear()


def _navegador() -> TestClient:
    """Outro navegador/dispositivo: cookies próprios, mesmo banco do teste."""
    return TestClient(app, base_url="https://testserver")


def _login(cliente, email, senha):
    return cliente.post("/auth/login", json={"email": email, "senha": senha})


def _cookie_decodificado(cliente) -> dict:
    return jwt.decode(
        cliente.cookies.get(COOKIE_NOME), settings.secret_key, algorithms=[ALGORITMO]
    )


@pytest.fixture
def admin(db, senha_hash_teste) -> Usuario:
    a = Usuario(
        nome="Admin",
        email=f"adm-{uuid4().hex}@example.org",
        senha_hash=senha_hash_teste,
        perfil="admin",
    )
    db.add(a)
    db.commit()
    return a


@pytest.fixture
def client_admin(client, admin, senha_teste) -> TestClient:
    assert _login(client, admin.email, senha_teste).status_code == 200
    return client


def test_token_novo_carrega_a_versao_do_usuario(client, db, usuario, senha_teste):
    _login(client, usuario.email, senha_teste)
    assert _cookie_decodificado(client)["v"] == 0

    usuario.token_versao = 3
    db.commit()
    outro = _navegador()
    _login(outro, usuario.email, senha_teste)
    assert _cookie_decodificado(outro)["v"] == 3


def test_trocar_senha_derruba_outros_dispositivos_e_mantem_este(
    client, usuario, senha_teste
):
    celular = _navegador()
    assert _login(celular, usuario.email, senha_teste).status_code == 200
    assert _login(client, usuario.email, senha_teste).status_code == 200

    r = client.post(
        "/auth/trocar-senha",
        json={"senha_atual": senha_teste, "senha_nova": NOVA_SENHA},
    )
    assert r.status_code == 204

    assert client.get("/auth/eu").status_code == 200  # quem trocou continua logado
    assert celular.get("/auth/eu").status_code == 401  # o outro dispositivo caiu


def test_redefinicao_pelo_admin_derruba_as_sessoes_do_alvo(
    client_admin, usuario, senha_teste
):
    celular = _navegador()
    assert _login(celular, usuario.email, senha_teste).status_code == 200

    r = client_admin.post(
        f"/usuarios/{usuario.id}/senha", json={"senha_nova": NOVA_SENHA}
    )
    assert r.status_code == 204
    assert celular.get("/auth/eu").status_code == 401
    assert _login(celular, usuario.email, NOVA_SENHA).status_code == 200


def test_desativar_e_reativar_nao_ressuscita_cookie_antigo(
    client_admin, usuario, senha_teste
):
    celular = _navegador()
    assert _login(celular, usuario.email, senha_teste).status_code == 200

    assert client_admin.patch(f"/usuarios/{usuario.id}", json={"ativo": False}).status_code == 200
    assert client_admin.patch(f"/usuarios/{usuario.id}", json={"ativo": True}).status_code == 200

    assert celular.get("/auth/eu").status_code == 401  # o cookie velho não volta a valer
    assert _login(celular, usuario.email, senha_teste).status_code == 200
    assert celular.get("/auth/eu").status_code == 200


def test_sair_de_todos_os_dispositivos(client, db, usuario, senha_teste):
    celular = _navegador()
    assert _login(celular, usuario.email, senha_teste).status_code == 200
    assert _login(client, usuario.email, senha_teste).status_code == 200

    assert client.post("/auth/sair-de-todos").status_code == 204

    assert client.get("/auth/eu").status_code == 401
    assert celular.get("/auth/eu").status_code == 401
    acoes = list(db.scalars(select(Auditoria.acao).where(Auditoria.usuario_id == usuario.id)))
    assert "sessoes_encerradas" in acoes


def test_sair_de_todos_exige_login(client):
    assert client.post("/auth/sair-de-todos").status_code == 401


def test_cookie_com_versao_antiga_e_recusado(client, db, usuario):
    usuario.token_versao = 1
    db.commit()

    client.cookies.set(COOKIE_NOME, criar_token(usuario.id, 0))
    assert client.get("/auth/eu").status_code == 401

    client.cookies.set(COOKIE_NOME, criar_token(usuario.id, 1))
    assert client.get("/auth/eu").status_code == 200


def test_token_sem_versao_vale_como_versao_zero(client, usuario):
    agora = datetime.now(timezone.utc)
    antigo = jwt.encode(
        {"sub": str(usuario.id), "iat": agora, "exp": agora + timedelta(minutes=5)},
        settings.secret_key,
        algorithm=ALGORITMO,
    )
    client.cookies.set(COOKIE_NOME, antigo)
    assert client.get("/auth/eu").status_code == 200


def test_token_assinado_com_outra_chave_e_recusado(client, usuario):
    agora = datetime.now(timezone.utc)
    falso = jwt.encode(
        {"sub": str(usuario.id), "v": 0, "exp": agora + timedelta(minutes=5)},
        "x" * 40,
        algorithm=ALGORITMO,
    )
    client.cookies.set(COOKIE_NOME, falso)
    assert client.get("/auth/eu").status_code == 401


def test_chave_curta_e_recusada_quando_cookie_seguro_esta_ligado():
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql://x", secret_key="curta", cookie_secure=True)
    ok = Settings(database_url="postgresql://x", secret_key="k" * 32, cookie_secure=True)
    assert ok.cookie_secure is True
    # em desenvolvimento (sem HTTPS) a chave curta continua aceita
    Settings(database_url="postgresql://x", secret_key="curta", cookie_secure=False)
