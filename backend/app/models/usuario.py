from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    senha_hash: Mapped[str] = mapped_column(Text)
    perfil: Mapped[str] = mapped_column(
        String(10), default="operador", server_default="operador"
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    token_versao: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
