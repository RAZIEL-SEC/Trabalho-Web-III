from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    __table_args__ = (
        CheckConstraint("tipo IN ('entrada', 'saida', 'estorno')"),
        CheckConstraint("quantidade > 0"),
        CheckConstraint(
            "(tipo = 'estorno') = (estorno_de IS NOT NULL)"
        ),
        CheckConstraint(
            "tipo <> 'estorno' OR motivo IS NOT NULL"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    item_id: Mapped[int] = mapped_column(
        ForeignKey("itens.id"),
    )

    tipo: Mapped[str] = mapped_column(String(10))

    quantidade: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
    )

    observacao: Mapped[str | None] = mapped_column(Text)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    estorno_de: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("movimentacoes.id"),
    )

    motivo: Mapped[str | None] = mapped_column(Text)