from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Item(Base):
    __tablename__ = "itens"
    __table_args__ = (
        CheckConstraint("unidade IN ('kg', 'g', 'un', 'l', 'ml', 'pacote', 'garrafa', 'frasco', 'lata', 'caixa', 'fardo', 'kit', 'par', 'rolo', 'duzia', 'bandeja', 'saco', 'galao')", name="ck_itens_unidade_valida"),
        CheckConstraint("saldo >= 0"),
        Index("uq_itens_nome_unidade_ativos", "nome", "unidade", unique=True, postgresql_where=text("ativo IS TRUE")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    unidade: Mapped[str] = mapped_column(String(10))
    subgrupo_id: Mapped[int] = mapped_column(ForeignKey("subgrupos_itens.id"), server_default=text("1"))
    saldo: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default=text("0"))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    criado_por: Mapped[int] = mapped_column()
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
