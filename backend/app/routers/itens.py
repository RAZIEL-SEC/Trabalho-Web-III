from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_usuario_atual
from app.models.item import Item
from app.models.usuario import Usuario

router = APIRouter(prefix="/itens", tags=["itens"])


class ItemIn(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    nome: str = Field(min_length=1, max_length=100)
    unidade: Literal["kg", "un", "l", "pacote"]


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    unidade: str
    saldo: Decimal
    ativo: bool
    criado_por: int
    criado_em: datetime


@router.post(
    "",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_item(
    dados: ItemIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    item = Item(
        nome=dados.nome,
        unidade=dados.unidade,
        criado_por=usuario.id,
    )

    db.add(item)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()

        if getattr(erro.orig, "sqlstate", None) == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um item com esse nome e unidade.",
            ) from erro

        raise

    db.refresh(item)
    return item


@router.get("", response_model=list[ItemOut])
def listar_itens(
    limite: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_atual),
):
    consulta = (
        select(Item)
        .order_by(Item.nome, Item.id)
        .offset(offset)
        .limit(limite)
    )

    return db.scalars(consulta).all()
