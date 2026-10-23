import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})
    return app.test_client()


def cadastrar_e_logar(c):
    c.post("/api/usuarios/cadastro", json={"nome": "Ana", "email": "ana@x.com", "senha": "123456"})
    return c.post("/api/usuarios/login", json={"email": "ana@x.com", "senha": "123456"})


def test_paginas(client):
    for url in ("/", "/login.html", "/cadastro.html", "/dashboard.html"):
        assert client.get(url).status_code == 200


def test_cadastro_duplicado(client):
    d = {"nome": "Ana", "email": "ana@x.com", "senha": "123456"}
    assert client.post("/api/usuarios/cadastro", json=d).status_code == 201
    assert client.post("/api/usuarios/cadastro", json=d).status_code == 409


def test_login_invalido(client):
    assert client.post("/api/usuarios/login", json={"email": "a@a.com", "senha": "x"}).status_code == 401


def test_listar_projetos_seed(client):
    assert len(client.get("/api/projetos").get_json()) >= 2


def test_doacao_exige_login(client):
    assert client.post("/api/doacoes", json={"projeto_id": 1, "valor": 10}).status_code == 401


def test_fluxo_doacao(client):
    assert cadastrar_e_logar(client).status_code == 200
    assert client.post("/api/doacoes", json={"projeto_id": 1, "valor": 25.5}).status_code == 201
    r = client.get("/api/doacoes/resumo").get_json()
    assert r["minhas_doacoes"] == 1 and r["meu_total"] == 25.5

