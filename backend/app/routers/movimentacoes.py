from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_usuario_atual
from app.models.item import Item
from app.models.movimentacao import Movimentacao
from app.models.usuario import Usuario
from app.services.estoque import (
    ConflitoEstoque,
    ItemNaoEncontrado,
    registrar_movimentacao,
)

router = APIRouter(prefix="/movimentacoes", tags=["movimentacoes"])


class MovimentacaoIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    item_id: int = Field(strict=True, gt=0, le=2147483647)
    tipo: Literal["entrada", "saida"]
    quantidade: Decimal = Field(
        gt=0, max_digits=10, decimal_places=2, allow_inf_nan=False
    )
    observacao: str | None = Field(default=None, max_length=1000)


class MovimentacaoOut(BaseModel):
    id: int
    item_id: int
    tipo: Literal["entrada", "saida"]
    quantidade: Decimal
    observacao: str | None
    usuario_id: int
    criado_em: datetime
    saldo_atual: Decimal


@router.post(
    "", response_model=MovimentacaoOut, status_code=status.HTTP_201_CREATED
)
def cadastrar_movimentacao(
    dados: MovimentacaoIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
) -> MovimentacaoOut:
    try:
        movimentacao, saldo_atual = registrar_movimentacao(
            db,
            item_id=dados.item_id,
            tipo=dados.tipo,
            quantidade=dados.quantidade,
            observacao=dados.observacao,
            usuario_id=usuario.id,
        )
        # Captura a resposta enquanto o bloqueio ainda está ativo, evitando
        # reler um saldo já modificado por outra requisição após o commit.
        resposta = MovimentacaoOut(
            id=movimentacao.id,
            item_id=movimentacao.item_id,
            tipo=movimentacao.tipo,
            quantidade=movimentacao.quantidade,
            observacao=movimentacao.observacao,
            usuario_id=movimentacao.usuario_id,
            criado_em=movimentacao.criado_em,
            saldo_atual=saldo_atual,
        )
        db.commit()
    except ItemNaoEncontrado as erro:
        db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(erro)) from erro
    except ConflitoEstoque as erro:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(erro)) from erro
    except SQLAlchemyError:
        db.rollback()
        raise

    return resposta


class MovimentacaoHistoricoOut(BaseModel):
    id: int
    item_id: int
    item_nome: str
    tipo: str
    quantidade: Decimal
    observacao: str | None
    usuario_id: int
    criado_em: datetime
    estorno_de: int | None
    motivo: str | None


@router.get("", response_model=list[MovimentacaoHistoricoOut])
def listar_movimentacoes(
    limite: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_atual),
):
    consulta = (
        select(Movimentacao, Item.nome)
        .join(Item, Item.id == Movimentacao.item_id)
        .order_by(Movimentacao.criado_em.desc(), Movimentacao.id.desc())
        .offset(offset)
        .limit(limite)
    )
    return [
        MovimentacaoHistoricoOut(
            id=mov.id,
            item_id=mov.item_id,
            item_nome=nome,
            tipo=mov.tipo,
            quantidade=mov.quantidade,
            observacao=mov.observacao,
            usuario_id=mov.usuario_id,
            criado_em=mov.criado_em,
            estorno_de=mov.estorno_de,
            motivo=mov.motivo,
        )
        for mov, nome in db.execute(consulta).all()
    ]
