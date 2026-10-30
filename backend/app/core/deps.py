from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import COOKIE_NOME, definir_cookie, ler_token
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
    usuario_id = ler_token(token) if token else None
    usuario = db.get(Usuario, usuario_id) if usuario_id else None
    if usuario is None or not usuario.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
    definir_cookie(response, usuario.id)  # renova: expira só por inatividade
    return usuario