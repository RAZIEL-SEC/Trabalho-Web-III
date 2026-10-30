import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_usuario_atual
from app.core.security import COOKIE_NOME, HASH_FALSO, definir_cookie, verificar_senha
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["auth"])

# limite simples em memória: 5 falhas por 10 min por IP + e-mail
JANELA_S, MAX_FALHAS = 600, 5
_falhas: dict[str, deque] = defaultdict(deque)


class LoginIn(BaseModel):
    email: str = Field(max_length=150)
    senha: str = Field(max_length=200)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str


def _checar_limite(chave: str) -> None:
    agora = time.monotonic()
    fila = _falhas[chave]
    while fila and agora - fila[0] > JANELA_S:
        fila.popleft()
    if len(fila) >= MAX_FALHAS:
        raise HTTPException(429, "Muitas tentativas. Aguarde alguns minutos.")


@router.post("/login", response_model=UsuarioOut)
def login(
    dados: LoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = dados.email.strip().lower()
    ip = request.client.host if request.client else "?"
    chave = f"{ip}|{email}"
    _checar_limite(chave)

    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    senha_ok = verificar_senha(dados.senha, usuario.senha_hash if usuario else HASH_FALSO)

    if not (usuario and usuario.ativo and senha_ok):
        _falhas[chave].append(time.monotonic())
        # mensagem genérica: não revela se o e-mail existe
        raise HTTPException(401, "E-mail ou senha incorretos")

    _falhas.pop(chave, None)
    definir_cookie(response, usuario.id)
    return usuario


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NOME, path="/")


@router.get("/eu", response_model=UsuarioOut)
def eu(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario