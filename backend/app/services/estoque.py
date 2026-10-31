from decimal import Decimal
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.movimentacao import Movimentacao

SALDO_MAXIMO = Decimal("99999999.99")
ESCALA_DECIMAL = Decimal("0.01")


class ItemNaoEncontrado(ValueError):
    pass


class ConflitoEstoque(ValueError):
    pass


def registrar_movimentacao(
    db: Session,
    *,
    item_id: int,
    tipo: Literal["entrada", "saida"],
    quantidade: Decimal,
    observacao: str | None,
    usuario_id: int,
) -> tuple[Movimentacao, Decimal]:
    """Prepara saldo e histórico; o chamador confirma ou reverte a transação."""
    item = db.scalar(
        select(Item)
        .where(Item.id == item_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if item is None:
        raise ItemNaoEncontrado("Item não encontrado.")
    if not item.ativo:
        raise ConflitoEstoque("Item inativo.")

    quantidade = quantidade.quantize(ESCALA_DECIMAL)
    saldo_atual = (
        item.saldo + quantidade if tipo == "entrada" else item.saldo - quantidade
    )
    if saldo_atual < 0:
        raise ConflitoEstoque("Saldo insuficiente para a saída.")
    if saldo_atual > SALDO_MAXIMO:
        raise ConflitoEstoque("Saldo máximo do item excedido.")

    item.saldo = saldo_atual
    movimentacao = Movimentacao(
        item_id=item.id,
        tipo=tipo,
        quantidade=quantidade,
        observacao=observacao,
        usuario_id=usuario_id,
    )
    db.add(movimentacao)
    db.flush()
    return movimentacao, saldo_atual
