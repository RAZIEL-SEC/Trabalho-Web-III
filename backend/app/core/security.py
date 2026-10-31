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


def criar_token(usuario_id: int, versao: int = 0) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "v": versao,  # versão da sessão: ver Usuario.token_versao
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO)


def ler_sessao(token: str) -> tuple[int, int] | None:
    """Devolve (usuario_id, versao) de um token válido, ou None."""
    try:
        dados = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
        # token sem "v" (emitido antes desta mudança) conta como versão 0
        return int(dados["sub"]), int(dados.get("v", 0))
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None


def ler_token(token: str) -> int | None:
    """Só o id do usuário (mantida por compatibilidade)."""
    sessao = ler_sessao(token)
    return sessao[0] if sessao else None


def definir_cookie(response: Response, usuario_id: int, versao: int = 0) -> None:
    response.set_cookie(
        COOKIE_NOME,
        criar_token(usuario_id, versao),
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )
