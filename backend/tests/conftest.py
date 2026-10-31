from collections.abc import Iterator
from pathlib import Path
from secrets import token_urlsafe
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema

from app.core.deps import get_db, get_usuario_atual
from app.core.security import gerar_hash
from app.db.session import engine
from app.main import app
from app.models.usuario import Usuario


@pytest.fixture(scope="session")
def senha_teste() -> str:
    return token_urlsafe(24)


@pytest.fixture(scope="session")
def senha_hash_teste(senha_teste: str) -> str:
    return gerar_hash(senha_teste)


@pytest.fixture
def db() -> Iterator[Session]:
    """Isola tabelas, dados e sequências sem tocar no schema público."""
    schema = f"test_itens_{uuid4().hex}"
    schema_sql = (
        Path(__file__).resolve().parents[2] / "database" / "schema.sql"
    ).read_text(encoding="utf-8")

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(CreateSchema(schema))
            # Sem public no search_path: uma tabela ausente deve causar erro.
            connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
            assert connection.scalar(text("SELECT current_schema()")) == schema
            connection.exec_driver_sql(schema_sql)

            # O commit/rollback real da rota opera em savepoints. A transação
            # externa continua aberta e desfaz inclusive o CREATE SCHEMA.
            with Session(
                bind=connection, join_transaction_mode="create_savepoint"
            ) as session:
                yield session
        finally:
            transaction.rollback()

        assert connection.scalar(
            text("SELECT to_regnamespace(:schema)"), {"schema": schema}
        ) is None


@pytest.fixture
def usuario(db: Session, senha_hash_teste: str) -> Usuario:
    usuario = Usuario(
        nome="Usuário de teste",
        email=f"itens-{uuid4().hex}@example.org",
        senha_hash=senha_hash_teste,
        ativo=True,
    )
    db.add(usuario)
    db.commit()
    return usuario


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    def get_db_teste() -> Iterator[Session]:
        yield db

    assert get_usuario_atual not in app.dependency_overrides
    overrides_anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = get_db_teste
    try:
        # HTTPS permite testar também quando COOKIE_SECURE está habilitado.
        with TestClient(app, base_url="https://testserver") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides_anteriores)


@pytest.fixture
def client_autenticado(
    client: TestClient, usuario: Usuario, senha_teste: str
) -> TestClient:
    response = client.post(
        "/auth/login", json={"email": usuario.email, "senha": senha_teste}
    )
    assert response.status_code == 200
    return client
