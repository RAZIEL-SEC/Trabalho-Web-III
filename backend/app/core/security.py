from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Response

from app.core.config import settings

COOKIE_NOME = "access_token"
ALGORITMO = "HS256"

_hasher = PasswordHasher()  # Argon2id por padrão
# hash falso: gasta o mesmo tempo quando o e-mail não existe
HASH_FALSO = _hasher.hash("senha-falsa-para-igualar-o-tempo")


def gerar_hash(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    try:
        return _hasher.verify(hash_, senha)
    except (VerifyMismatchError, InvalidHashError):
        return False


def criar_token(usuario_id: int) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO)


def ler_token(token: str) -> int | None:
    try:
        dados = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
        return int(dados["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def definir_cookie(response: Response, usuario_id: int) -> None:
    response.set_cookie(
        COOKIE_NOME,
        criar_token(usuario_id),
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )