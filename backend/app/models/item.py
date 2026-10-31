from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Item(Base):
    __tablename__ = "itens"

    __table_args__ = (
        CheckConstraint("unidade IN ('kg', 'un', 'l', 'pacote')"),
        CheckConstraint("saldo >= 0"),
        UniqueConstraint("nome", "unidade"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    unidade: Mapped[str] = mapped_column(String(10))

    saldo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        server_default=text("0"),
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
    )

    criado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )