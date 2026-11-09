from fastapi.testclient import TestClient


def test_rejeita_origem_externa_no_login(client, usuario, senha_teste):
    response = client.post(
        "/auth/login",
        headers={"Origin": "https://evil.example"},
        json={"email": usuario.email, "senha": senha_teste},
    )
    assert response.status_code == 403


def test_rejeita_mutacao_autenticada_sem_token_csrf(client_autenticado):
    response = client_autenticado.post(
        "/auth/sair-de-todos",
        headers={"Origin": "https://testserver", "X-CSRF-Token": ""},
    )
    assert response.status_code == 403


def test_rejeita_origem_externa_mesmo_com_token_csrf(client_autenticado):
    token = client_autenticado.get("/auth/csrf").json()["csrf_token"]
    response = client_autenticado.post(
        "/auth/sair-de-todos",
        headers={"Origin": "https://evil.example", "X-CSRF-Token": token},
    )
    assert response.status_code == 403


def test_token_csrf_valido_permite_mutacao(client_autenticado):
    token = client_autenticado.get("/auth/csrf").json()["csrf_token"]
    response = client_autenticado.post(
        "/auth/sair-de-todos",
        headers={"Origin": "https://testserver", "X-CSRF-Token": token},
    )
    assert response.status_code == 204
