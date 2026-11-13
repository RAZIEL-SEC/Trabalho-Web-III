from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_usuario_atual
from app.models.grupo_item import GrupoItem, SubgrupoItem
from app.models.item import Item
from app.models.usuario import Usuario
from app.services.protecao_api import limitar_api

router = APIRouter(prefix="/classificacoes", tags=["classificacoes"], dependencies=[Depends(limitar_api)])

class NomeIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    nome: str = Field(min_length=1, max_length=80)

class GrupoIn(NomeIn):
    pass

class SubgrupoIn(NomeIn):
    grupo_id: int = Field(gt=0)

class GrupoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    ativo: bool
    criado_em: datetime

class SubgrupoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    grupo_id: int
    nome: str
    ativo: bool
    criado_em: datetime

@router.get("/grupos", response_model=list[GrupoOut])
def listar_grupos(db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    return db.scalars(select(GrupoItem).where(GrupoItem.ativo.is_(True)).order_by(GrupoItem.nome)).all()

@router.post("/grupos", response_model=GrupoOut, status_code=201)
def criar_grupo(dados: GrupoIn, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    grupo = GrupoItem(nome=dados.nome)
    db.add(grupo)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Já existe um grupo com esse nome.") from erro
    db.refresh(grupo)
    return grupo

@router.patch("/grupos/{grupo_id}", response_model=GrupoOut)
def editar_grupo(grupo_id: int, dados: GrupoIn, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    grupo = db.get(GrupoItem, grupo_id)
    if not grupo or not grupo.ativo:
        raise HTTPException(404, "Grupo não encontrado.")
    grupo.nome = dados.nome
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Já existe um grupo com esse nome.") from erro
    db.refresh(grupo)
    return grupo

@router.delete("/grupos/{grupo_id}", status_code=204)
def desativar_grupo(grupo_id: int, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    grupo = db.get(GrupoItem, grupo_id)
    if not grupo or not grupo.ativo:
        raise HTTPException(404, "Grupo não encontrado.")
    if db.scalar(select(SubgrupoItem.id).where(SubgrupoItem.grupo_id == grupo_id, SubgrupoItem.ativo.is_(True)).limit(1)):
        raise HTTPException(409, "Desative ou transfira os subgrupos antes de desativar este grupo.")
    grupo.ativo = False
    db.commit()

@router.get("/subgrupos", response_model=list[SubgrupoOut])
def listar_subgrupos(grupo_id: int | None = None, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    consulta = select(SubgrupoItem).join(GrupoItem).where(SubgrupoItem.ativo.is_(True), GrupoItem.ativo.is_(True))
    if grupo_id is not None:
        consulta = consulta.where(SubgrupoItem.grupo_id == grupo_id)
    return db.scalars(consulta.order_by(SubgrupoItem.nome)).all()

@router.post("/subgrupos", response_model=SubgrupoOut, status_code=201)
def criar_subgrupo(dados: SubgrupoIn, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    grupo = db.get(GrupoItem, dados.grupo_id)
    if not grupo or not grupo.ativo:
        raise HTTPException(404, "Grupo não encontrado ou inativo.")
    subgrupo = SubgrupoItem(nome=dados.nome, grupo_id=dados.grupo_id)
    db.add(subgrupo)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Já existe um subgrupo com esse nome neste grupo.") from erro
    db.refresh(subgrupo)
    return subgrupo

@router.patch("/subgrupos/{subgrupo_id}", response_model=SubgrupoOut)
def editar_subgrupo(subgrupo_id: int, dados: SubgrupoIn, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    subgrupo = db.get(SubgrupoItem, subgrupo_id)
    grupo = db.get(GrupoItem, dados.grupo_id)
    if not subgrupo or not subgrupo.ativo:
        raise HTTPException(404, "Subgrupo não encontrado.")
    if not grupo or not grupo.ativo:
        raise HTTPException(404, "Grupo não encontrado ou inativo.")
    subgrupo.nome, subgrupo.grupo_id = dados.nome, dados.grupo_id
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Já existe um subgrupo com esse nome neste grupo.") from erro
    db.refresh(subgrupo)
    return subgrupo

@router.delete("/subgrupos/{subgrupo_id}", status_code=204)
def desativar_subgrupo(subgrupo_id: int, db: Session = Depends(get_db), _usuario: Usuario = Depends(get_usuario_atual)):
    subgrupo = db.get(SubgrupoItem, subgrupo_id)
    if not subgrupo or not subgrupo.ativo:
        raise HTTPException(404, "Subgrupo não encontrado.")
    if db.scalar(select(Item.id).where(Item.subgrupo_id == subgrupo_id, Item.ativo.is_(True)).limit(1)):
        raise HTTPException(409, "Este subgrupo possui itens ativos. Reclassifique-os antes de desativá-lo.")
    subgrupo.ativo = False
    db.commit()
