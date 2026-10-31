from sqlalchemy.orm import Session

from app.models.usuario import Usuario


def invalidar_sessoes(usuario: Usuario) -> None:
    """Sobe a versão do token: todo cookie emitido antes deixa de valer.

    Quem chama faz o commit. Para manter a sessão atual viva, emita um cookie novo
    depois do commit (db.refresh(usuario) traz a versão nova).
    """
    usuario.token_versao = Usuario.token_versao + 1
