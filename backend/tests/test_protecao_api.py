from fastapi.testclient import TestClient

from app.core.config import settings


def test_rate_limit_por_usuario_retorna_429(
    client_autenticado: TestClient, monkeypatch
):
    monkeypatch.setattr(settings, "api_rate_limit_user_per_minute", 2)
    monkeypatch.setattr(settings, "api_rate_limit_ip_per_minute", 100)

    primeira = client_autenticado.get("/itens")
    segunda = client_autenticado.get("/itens")
    terceira = client_autenticado.get("/itens")

    assert primeira.status_code == segunda.status_code == 200
    assert terceira.status_code == 429
    assert terceira.headers["retry-after"] == "60"
    assert terceira.json()["detail"] == (
        "Limite de requisições excedido. Aguarde um minuto."
    )


def test_rate_limit_nao_afeta_usuario_diferente(
    client_autenticado: TestClient, db, senha_hash_teste: str,
    senha_teste: str, monkeypatch,
):
    from uuid import uuid4

    from app.models.usuario import Usuario

    monkeypatch.setattr(settings, "api_rate_limit_user_per_minute", 1)
    monkeypatch.setattr(settings, "api_rate_limit_ip_per_minute", 100)

    assert client_autenticado.get("/itens").status_code == 200
    assert client_autenticado.get("/itens").status_code == 429

    outro = Usuario(
        nome="Segundo usuário",
        email=f"rate-limit-{uuid4().hex}@example.org",
        senha_hash=senha_hash_teste,
        ativo=True,
    )
    db.add(outro)
    db.commit()

    # A sessão de teste é compartilhada com o cliente; troca o cookie por
    # um login real para comprovar o bucket separado por usuário.
    login = client_autenticado.post(
        "/auth/login", json={"email": outro.email, "senha": senha_teste}
    )
    assert login.status_code == 200
    assert client_autenticado.get("/itens").status_code == 200
