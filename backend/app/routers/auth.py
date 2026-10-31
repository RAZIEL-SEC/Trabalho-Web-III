import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_usuario_atual
from app.core.security import (
    COOKIE_NOME,
    HASH_FALSO,
    definir_cookie,
    gerar_hash,
    verificar_senha,
)
from app.models.usuario import Usuario
from app.services.auditoria import ip_do_cliente, registrar
from app.services.sessoes import invalidar_sessoes

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
    perfil: str


class TrocarSenhaIn(BaseModel):
    senha_atual: str = Field(max_length=200)
    senha_nova: str = Field(min_length=10, max_length=200)


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
    ip = ip_do_cliente(request)
    chave = f"{ip}|{email}"
    _checar_limite(chave)

    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    senha_ok = verificar_senha(dados.senha, usuario.senha_hash if usuario else HASH_FALSO)

    if not (usuario and usuario.ativo and senha_ok):
        _falhas[chave].append(time.monotonic())
        # e-mail desconhecido não é gravado: poderia ser uma senha digitada no campo errado
        registrar(db, usuario.id if usuario else None, "login_falha", None, ip)
        db.commit()
        # mensagem genérica: não revela se o e-mail existe
        raise HTTPException(401, "E-mail ou senha incorretos")

    _falhas.pop(chave, None)
    registrar(db, usuario.id, "login_ok", None, ip)
    db.commit()
    definir_cookie(response, usuario.id, usuario.token_versao)
    return usuario


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NOME, path="/")


@router.get("/eu", response_model=UsuarioOut)
def eu(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario


@router.post("/trocar-senha", status_code=204)
def trocar_senha(
    dados: TrocarSenhaIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(400, "Senha atual incorreta")
    if dados.senha_nova == dados.senha_atual:
        raise HTTPException(400, "A nova senha deve ser diferente da atual")
    usuario.senha_hash = gerar_hash(dados.senha_nova)
    invalidar_sessoes(usuario)  # derruba as sessões de outros dispositivos
    registrar(db, usuario.id, "senha_alterada", None, ip_do_cliente(request))
    db.commit()
    db.refresh(usuario)
    # esta sessão continua: recebe um cookie com a versão nova
    definir_cookie(response, usuario.id, usuario.token_versao)


@router.post("/sair-de-todos", status_code=204)
def sair_de_todos(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    """Encerra todas as sessões abertas, inclusive esta."""
    invalidar_sessoes(usuario)
    registrar(db, usuario.id, "sessoes_encerradas", None, ip_do_cliente(request))
    db.commit()
    response.delete_cookie(COOKIE_NOME, path="/")
