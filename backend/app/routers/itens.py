from datetime import datetime
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_usuario_atual
from app.models.grupo_item import GrupoItem, SubgrupoItem
from app.models.item import Item
from app.models.usuario import Usuario
from app.services.protecao_api import limitar_api

router = APIRouter(prefix="/itens", tags=["itens"], dependencies=[Depends(limitar_api)])

class ItemIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    nome: str = Field(min_length=1, max_length=100)
    unidade: Literal["kg", "g", "un", "l", "ml", "pacote", "garrafa", "frasco", "lata", "caixa", "fardo", "kit", "par", "rolo", "duzia", "bandeja", "saco", "galao"]
    subgrupo_id: int | None = Field(default=None, gt=0)
    grupo_id: int | None = Field(default=None, gt=0)

class ItemClassificacaoIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subgrupo_id: int | None = Field(default=None, gt=0)
    grupo_id: int | None = Field(default=None, gt=0)

class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    unidade: str
    subgrupo_id: int
    saldo: Decimal
    ativo: bool
    criado_por: int
    criado_em: datetime

def _subgrupo_padrao_do_grupo(db: Session, grupo_id: int) -> SubgrupoItem:
    grupo = db.scalar(select(GrupoItem).where(GrupoItem.id == grupo_id).with_for_update())
    if not grupo or not grupo.ativo:
        raise HTTPException(422, "Selecione um grupo ativo.")
    subgrupo = db.scalar(select(SubgrupoItem).where(
        SubgrupoItem.grupo_id == grupo_id,
        SubgrupoItem.nome == "Sem subgrupo",
        SubgrupoItem.ativo.is_(True),
    ))
    if subgrupo is None:
        subgrupo = SubgrupoItem(nome="Sem subgrupo", grupo_id=grupo_id)
        db.add(subgrupo)
        db.flush()
    return subgrupo

def _resolver_classificacao(db: Session, subgrupo_id: int | None, grupo_id: int | None) -> SubgrupoItem:
    if subgrupo_id is not None:
        subgrupo = db.get(SubgrupoItem, subgrupo_id)
        grupo = db.get(GrupoItem, subgrupo.grupo_id) if subgrupo else None
        if not subgrupo or not subgrupo.ativo or not grupo or not grupo.ativo:
            raise HTTPException(422, "Selecione um subgrupo ativo.")
        if grupo_id is not None and grupo.id != grupo_id:
            raise HTTPException(422, "O subgrupo selecionado não pertence ao grupo informado.")
        return subgrupo
    if grupo_id is not None:
        return _subgrupo_padrao_do_grupo(db, grupo_id)
    # Compatibilidade com cadastros antigos que não enviam classificação.
    subgrupo = db.scalar(select(SubgrupoItem).join(GrupoItem).where(
        SubgrupoItem.nome == "Sem classificação",
        GrupoItem.nome == "Sem classificação",
        SubgrupoItem.ativo.is_(True),
        GrupoItem.ativo.is_(True),
    ))
    if subgrupo is None:
        raise HTTPException(422, "Selecione um grupo ou subgrupo ativo.")
    return subgrupo

@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def cadastrar_item(dados: ItemIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_atual)):
    subgrupo = _resolver_classificacao(db, dados.subgrupo_id, dados.grupo_id)
    item = Item(nome=dados.nome, unidade=dados.unidade, subgrupo_id=subgrupo.id, criado_por=usuario.id)
    db.add(item)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        if getattr(erro.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, "Já existe um item ativo com esse nome e unidade.") from erro
        raise
    db.refresh(item)
    return item

@router.get("", response_model=list[ItemOut])
def listar_itens(limite: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    consulta = select(Item).where(Item.ativo.is_(True)).order_by(Item.nome, Item.id).offset(offset).limit(limite)
    return db.scalars(consulta).all()

@router.delete("/{item_id}", response_model=ItemOut)
def excluir_item(item_id: int, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    item = db.scalar(select(Item).where(Item.id == item_id).with_for_update())
    if item is None or not item.ativo:
        raise HTTPException(404, "Item não encontrado.")
    item.ativo = False
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{item_id}/classificacao", response_model=ItemOut)
def reclassificar_item(item_id: int, dados: ItemClassificacaoIn, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    if dados.subgrupo_id is None and dados.grupo_id is None:
        raise HTTPException(422, "Informe um grupo ou subgrupo.")
    item = db.scalar(select(Item).where(Item.id == item_id).with_for_update())
    if item is None or not item.ativo:
        raise HTTPException(404, "Item não encontrado.")
    subgrupo = _resolver_classificacao(db, dados.subgrupo_id, dados.grupo_id)
    item.subgrupo_id = subgrupo.id
    db.commit()
    db.refresh(item)
    return item
