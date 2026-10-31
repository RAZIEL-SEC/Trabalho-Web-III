from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import COOKIE_NOME, definir_cookie, ler_sessao
from app.db.session import SessionLocal
from app.models.usuario import Usuario


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_usuario_atual(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> Usuario:
    """Dependência que protege as rotas internas. O Daniel usa nos routers."""
    token = request.cookies.get(COOKIE_NOME)
    sessao = ler_sessao(token) if token else None
    usuario = db.get(Usuario, sessao[0]) if sessao else None
    if (
        usuario is None
        or not usuario.ativo
        or usuario.token_versao != sessao[1]  # sessão encerrada em outro lugar
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
    definir_cookie(response, usuario.id, usuario.token_versao)  # renova: expira só por inatividade
    return usuario

def get_admin_atual(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    """Rotas de administração (cadastro de usuários)."""
    if usuario.perfil != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a administradores")
    return usuario
