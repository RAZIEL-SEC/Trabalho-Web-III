import hashlib
import hmac
from urllib.parse import urlsplit

from fastapi import Request

from app.core.config import settings
from app.core.security import COOKIE_NOME, ler_sessao

METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}


def token_csrf(usuario_id: int, versao: int) -> str:
    mensagem = f"csrf:{usuario_id}:{versao}".encode("utf-8")
    return hmac.new(settings.secret_key.encode("utf-8"), mensagem, hashlib.sha256).hexdigest()


def _origem_da_url(valor: str) -> str | None:
    try:
        partes = urlsplit(valor)
        if partes.scheme not in {"http", "https"} or not partes.netloc:
            return None
        if partes.username is not None or partes.password is not None:
            return None
        return f"{partes.scheme.lower()}://{partes.netloc.lower()}"
    except ValueError:
        return None


def origem_permitida(request: Request) -> bool:
    recebido = request.headers.get("origin")
    if recebido is not None:
        origem = _origem_da_url(recebido)
        if origem is None:
            return False
    else:
        referer = request.headers.get("referer")
        origem = _origem_da_url(referer) if referer else None
        if origem is None:
            return False
    atual = f"{request.url.scheme.lower()}://{request.url.netloc.lower()}"
    return origem in {atual, *settings.trusted_csrf_origins}


def validar_requisicao_csrf(request: Request) -> bool:
    if request.method.upper() in METODOS_SEGUROS:
        return True
    if not origem_permitida(request):
        return False
    # Login pode ocorrer enquanto o navegador ainda envia um cookie antigo.
    # A origem continua obrigatória, mas não há token da sessão anterior a exigir.
    if request.url.path == "/auth/login":
        return True
    cookie = request.cookies.get(COOKIE_NOME)
    sessao = ler_sessao(cookie) if cookie else None
    if sessao is None:
        return True
    recebido = request.headers.get("x-csrf-token", "")
    esperado = token_csrf(sessao[0], sessao[1])
    return bool(recebido) and hmac.compare_digest(recebido, esperado)
