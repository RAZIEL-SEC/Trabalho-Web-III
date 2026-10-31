from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_admin_atual, get_db
from app.core.security import gerar_hash
from app.models.usuario import Usuario
from app.services.auditoria import ip_do_cliente, registrar
from app.services.sessoes import invalidar_sessoes

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

Perfil = Literal["admin", "operador"]
EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioCriarIn(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=150, pattern=EMAIL_RE)
    senha: str = Field(min_length=10, max_length=200)
    perfil: Perfil = "operador"

    @field_validator("nome", mode="before")
    @classmethod
    def _limpar_nome(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email", mode="before")
    @classmethod
    def _normalizar_email(cls, v):
        return v.strip().lower() if isinstance(v, str) else v


class UsuarioAtualizarIn(BaseModel):
    ativo: bool | None = None
    perfil: Perfil | None = None


class SenhaNovaIn(BaseModel):
    senha_nova: str = Field(min_length=10, max_length=200)


class UsuarioAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool
    criado_em: datetime


@router.post("", response_model=UsuarioAdminOut, status_code=201)
def criar(
    dados: UsuarioCriarIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_atual),
):
    if db.scalar(select(Usuario.id).where(Usuario.email == dados.email)):
        raise HTTPException(409, "Já existe um usuário com esse e-mail")

    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash(dados.senha),
        perfil=dados.perfil,
    )
    db.add(novo)
    try:
        db.flush()
    except IntegrityError:  # dois cadastros do mesmo e-mail ao mesmo tempo
        db.rollback()
        raise HTTPException(409, "Já existe um usuário com esse e-mail")

    registrar(
        db, admin.id, "usuario_criado",
        f"id={novo.id} perfil={novo.perfil}", ip_do_cliente(request),
    )
    db.commit()
    return novo


@router.get("", response_model=list[UsuarioAdminOut])
def listar(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_admin_atual),
):
    return db.scalars(select(Usuario).order_by(Usuario.nome, Usuario.id)).all()


@router.patch("/{usuario_id}", response_model=UsuarioAdminOut)
def atualizar(
    usuario_id: int,
    dados: UsuarioAtualizarIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_atual),
):
    alvo = db.get(Usuario, usuario_id)
    if alvo is None:
        raise HTTPException(404, "Usuário não encontrado")

    # evita que o último administrador se tranque para fora do sistema
    if alvo.id == admin.id and (
        dados.ativo is False or (dados.perfil is not None and dados.perfil != "admin")
    ):
        raise HTTPException(400, "Você não pode desativar nem rebaixar a própria conta")

    mudancas = []
    if dados.ativo is not None and dados.ativo != alvo.ativo:
        alvo.ativo = dados.ativo
        mudancas.append(f"ativo={dados.ativo}")
        if not dados.ativo:
            invalidar_sessoes(alvo)  # reativar depois não ressuscita cookies antigos
    if dados.perfil is not None and dados.perfil != alvo.perfil:
        alvo.perfil = dados.perfil
        mudancas.append(f"perfil={dados.perfil}")

    if mudancas:
        registrar(
            db, admin.id, "usuario_atualizado",
            f"id={alvo.id} " + " ".join(mudancas), ip_do_cliente(request),
        )
        db.commit()
    return alvo


@router.post("/{usuario_id}/senha", status_code=204)
def redefinir_senha(
    usuario_id: int,
    dados: SenhaNovaIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_atual),
):
    alvo = db.get(Usuario, usuario_id)
    if alvo is None:
        raise HTTPException(404, "Usuário não encontrado")
    alvo.senha_hash = gerar_hash(dados.senha_nova)
    invalidar_sessoes(alvo)
    registrar(db, admin.id, "senha_redefinida", f"id={alvo.id}", ip_do_cliente(request))
    db.commit()
