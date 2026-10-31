from fastapi import Request
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria


def ip_do_cliente(request: Request) -> str | None:
    return request.client.host if request.client else None


def registrar(
    db: Session,
    usuario_id: int | None,
    acao: str,
    detalhe: str | None = None,
    ip: str | None = None,
) -> None:
    """Adiciona uma linha ao log. Quem chama faz o commit, junto da ação."""
    db.add(Auditoria(usuario_id=usuario_id, acao=acao, detalhe=detalhe, ip=ip))
