from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class GrupoItem(Base):
    __tablename__ = "grupos_itens"
    __table_args__ = (
        Index("uq_grupos_itens_nome_ativo", "nome", unique=True, postgresql_where=text("ativo IS TRUE")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class SubgrupoItem(Base):
    __tablename__ = "subgrupos_itens"
    __table_args__ = (
        Index("uq_subgrupos_grupo_nome_ativo", "grupo_id", "nome", unique=True, postgresql_where=text("ativo IS TRUE")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupos_itens.id"))
    nome: Mapped[str] = mapped_column(String(80))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
