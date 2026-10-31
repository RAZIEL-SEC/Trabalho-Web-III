from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import COOKIE_NOME
from app.models.item import Item
from app.models.usuario import Usuario


def quantidade_itens(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Item))


@pytest.mark.parametrize("metodo", ["GET", "POST"])
def test_itens_exigem_autenticacao(client: TestClient, db: Session, metodo: str):
    kwargs = {"json": {"nome": "Arroz", "unidade": "kg"}} if metodo == "POST" else {}
    response = client.request(metodo, "/itens", **kwargs)

    assert response.status_code == 401
    assert response.json() == {"detail": "Não autenticado"}
    assert quantidade_itens(db) == 0


def test_login_real_permite_acesso_por_cookie(
    client: TestClient, usuario: Usuario, senha_teste: str
):
    response = client.post(
        "/auth/login", json={"email": usuario.email, "senha": senha_teste}
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": "operador",
    }
    assert client.cookies.get(COOKIE_NOME)
    cookie = next(cookie for cookie in client.cookies.jar if cookie.name == COOKIE_NOME)
    assert cookie.has_nonstandard_attr("HttpOnly")
    assert cookie.get_nonstandard_attr("SameSite").lower() == "strict"
    assert cookie.path == "/"
    assert client.get("/itens").status_code == 200
    assert client.post(
        "/itens", json={"nome": "Arroz", "unidade": "kg"}
    ).status_code == 201


def test_login_invalido_nao_libera_acesso(
    client: TestClient, usuario: Usuario, senha_teste: str
):
    response = client.post(
        "/auth/login", json={"email": usuario.email, "senha": senha_teste + "errada"}
    )

    assert response.status_code == 401
    assert not client.cookies.get(COOKIE_NOME)
    assert client.get("/itens").status_code == 401
    assert client.post(
        "/itens", json={"nome": "Arroz", "unidade": "kg"}
    ).status_code == 401


@pytest.mark.parametrize("metodo", ["GET", "POST"])
def test_cookie_invalido_nao_libera_acesso(client: TestClient, metodo: str):
    client.cookies.set(COOKIE_NOME, "cookie-invalido")
    kwargs = {"json": {"nome": "Arroz", "unidade": "kg"}} if metodo == "POST" else {}

    assert client.request(metodo, "/itens", **kwargs).status_code == 401


@pytest.mark.parametrize("metodo", ["GET", "POST"])
def test_usuario_inativo_perde_acesso(
    client_autenticado: TestClient, db: Session, usuario: Usuario, metodo: str
):
    usuario.ativo = False
    db.commit()
    kwargs = {"json": {"nome": "Arroz", "unidade": "kg"}} if metodo == "POST" else {}

    assert client_autenticado.request(metodo, "/itens", **kwargs).status_code == 401
    assert quantidade_itens(db) == 0


@pytest.mark.parametrize("unidade", ["kg", "un", "l", "pacote"])
def test_cadastro_persiste_dados_e_defaults(
    client_autenticado: TestClient, db: Session, usuario: Usuario, unidade: str
):
    response = client_autenticado.post(
        "/itens", json={"nome": "  Arroz  ", "unidade": unidade}
    )

    assert response.status_code == 201
    dados = response.json()
    assert set(dados) == {
        "id", "nome", "unidade", "saldo", "ativo", "criado_por", "criado_em"
    }
    assert dados["nome"] == "Arroz"
    assert dados["unidade"] == unidade
    assert dados["saldo"] == "0.00"
    assert dados["ativo"] is True
    assert dados["criado_por"] == usuario.id
    assert datetime.fromisoformat(dados["criado_em"]).tzinfo is not None

    # Recarrega do PostgreSQL, sem depender do objeto retornado pela rota.
    db.expire_all()
    item = db.get(Item, dados["id"])
    assert item is not None
    assert item.nome == "Arroz"
    assert item.unidade == unidade
    assert item.saldo == Decimal("0.00")
    assert item.ativo is True
    assert item.criado_por == usuario.id
    assert item.criado_em == datetime.fromisoformat(dados["criado_em"])
    assert quantidade_itens(db) == 1


def test_duplicidade_retorna_409_e_faz_rollback(
    client_autenticado: TestClient, db: Session
):
    original = client_autenticado.post(
        "/itens", json={"nome": "Arroz", "unidade": "kg"}
    )
    assert original.status_code == 201

    response = client_autenticado.post(
        "/itens", json={"nome": "  Arroz  ", "unidade": "kg"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe um item com esse nome e unidade."}
    # Sem db.rollback() na rota, a sessão fica inválida após o IntegrityError.
    assert db.is_active
    assert quantidade_itens(db) == 1
    assert db.get(Item, original.json()["id"]).nome == "Arroz"
    assert client_autenticado.get("/itens").json() == [original.json()]

    novo = client_autenticado.post(
        "/itens", json={"nome": "Feijão", "unidade": "kg"}
    )
    assert novo.status_code == 201
    assert quantidade_itens(db) == 2


def test_cadastro_usa_usuario_do_cookie(
    client_autenticado: TestClient,
    db: Session,
    usuario: Usuario,
    senha_hash_teste: str,
    senha_teste: str,
):
    outro_usuario = Usuario(
        nome="Outro usuário de teste",
        email="outro@example.org",
        senha_hash=senha_hash_teste,
        ativo=True,
    )
    db.add(outro_usuario)
    db.commit()
    assert outro_usuario.id != usuario.id

    login = client_autenticado.post(
        "/auth/login", json={"email": outro_usuario.email, "senha": senha_teste}
    )
    assert login.status_code == 200
    response = client_autenticado.post(
        "/itens", json={"nome": "Arroz", "unidade": "kg"}
    )

    assert response.status_code == 201
    assert response.json()["criado_por"] == outro_usuario.id
    db.expire_all()
    assert db.get(Item, response.json()["id"]).criado_por == outro_usuario.id


def test_mesmo_nome_com_unidades_diferentes_e_permitido(
    client_autenticado: TestClient, db: Session
):
    for unidade in ("kg", "pacote"):
        response = client_autenticado.post(
            "/itens", json={"nome": "Arroz", "unidade": unidade}
        )
        assert response.status_code == 201

    assert quantidade_itens(db) == 2


@pytest.mark.parametrize(
    "dados",
    [
        pytest.param({"nome": "", "unidade": "kg"}, id="nome-vazio"),
        pytest.param({"nome": " \t\n ", "unidade": "kg"}, id="nome-em-branco"),
        pytest.param({"nome": "a" * 101, "unidade": "kg"}, id="nome-longo"),
        pytest.param({"nome": None, "unidade": "kg"}, id="nome-nulo"),
        pytest.param({"nome": 123, "unidade": "kg"}, id="nome-numerico"),
        pytest.param({"unidade": "kg"}, id="nome-ausente"),
        pytest.param({"nome": "Arroz"}, id="unidade-ausente"),
        pytest.param({"nome": "Arroz", "unidade": None}, id="unidade-nula"),
        pytest.param({"nome": "Arroz", "unidade": "caixa"}, id="unidade-invalida"),
        pytest.param({"nome": "Arroz", "unidade": "KG"}, id="unidade-maiuscula"),
        *[
            pytest.param(
                {"nome": "Arroz", "unidade": "kg", campo: valor}, id=f"extra-{campo}"
            )
            for campo, valor in (
                ("saldo", "10.00"),
                ("ativo", False),
                ("criado_por", 999),
                ("id", 999),
                ("criado_em", "2026-01-01T00:00:00Z"),
                ("outro", "valor"),
            )
        ],
    ],
)
def test_entrada_invalida_nao_cria_registros(
    client_autenticado: TestClient, db: Session, dados: dict
):
    quantidade_antes = quantidade_itens(db)

    response = client_autenticado.post("/itens", json=dados)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert quantidade_itens(db) == quantidade_antes
    assert client_autenticado.get("/itens").json() == []


def test_nome_com_100_caracteres_e_aceito(client_autenticado: TestClient):
    response = client_autenticado.post(
        "/itens", json={"nome": "a" * 100, "unidade": "kg"}
    )

    assert response.status_code == 201
    assert response.json()["nome"] == "a" * 100


def test_listagem_ordena_por_nome_e_id(client_autenticado: TestClient):
    cadastrados = []
    for nome, unidade in (
        ("Feijão", "kg"), ("Arroz", "pacote"), ("Arroz", "kg"), ("Leite", "l")
    ):
        response = client_autenticado.post(
            "/itens", json={"nome": nome, "unidade": unidade}
        )
        assert response.status_code == 201
        cadastrados.append(response.json())

    response = client_autenticado.get("/itens")

    assert response.status_code == 200
    assert response.json() == sorted(cadastrados, key=lambda item: (item["nome"], item["id"]))
    assert all(isinstance(item["saldo"], str) for item in response.json())


@pytest.mark.parametrize(
    "parametros,inicio,fim",
    [
        pytest.param({}, 0, 100, id="limite-padrao-100"),
        pytest.param({"limite": 200}, 0, 200, id="limite-maximo-200"),
        pytest.param({"limite": 2, "offset": 1}, 1, 3, id="pagina-intermediaria"),
        pytest.param({"limite": 1, "offset": 204}, 204, 205, id="ultimo-item"),
        pytest.param({"offset": 205}, 205, 205, id="pagina-vazia"),
    ],
)
def test_listagem_respeita_paginacao(
    client_autenticado: TestClient,
    db: Session,
    usuario: Usuario,
    parametros: dict,
    inicio: int,
    fim: int,
):
    itens = [
        Item(nome=f"Item {indice:03}", unidade="un", criado_por=usuario.id)
        for indice in range(205)
    ]
    db.add_all(itens)
    db.commit()
    ids_esperados = [item.id for item in itens[inicio:fim]]

    response = client_autenticado.get("/itens", params=parametros)

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ids_esperados


@pytest.mark.parametrize(
    "parametros",
    [
        {"limite": 0}, {"limite": -1}, {"limite": 201}, {"limite": "abc"},
        {"offset": -1}, {"offset": "abc"},
    ],
)
def test_paginacao_invalida_retorna_422(client_autenticado: TestClient, parametros: dict):
    assert client_autenticado.get("/itens", params=parametros).status_code == 422
