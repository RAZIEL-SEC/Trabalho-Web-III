import sqlite3

from flask import Blueprint, jsonify, request, session

from models import usuario

bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@bp.post("/cadastro")
def cadastro():
    d = request.get_json(silent=True) or {}
    nome, email, senha = (d.get("nome") or "").strip(), (d.get("email") or "").strip(), d.get("senha") or ""
    if not nome or "@" not in email or len(senha) < 6:
        return jsonify(erro="Informe nome, e-mail válido e senha (mín. 6 caracteres)."), 400
    try:
        uid = usuario.criar(nome, email, senha)
    except sqlite3.IntegrityError:
        return jsonify(erro="E-mail já cadastrado."), 409
    return jsonify(id=uid, nome=nome, email=email.lower()), 201


@bp.post("/login")
def login():
    d = request.get_json(silent=True) or {}
    u = usuario.autenticar(d.get("email") or "", d.get("senha") or "")
    if not u:
        return jsonify(erro="E-mail ou senha incorretos."), 401
    session["user_id"] = u["id"]
    return jsonify(id=u["id"], nome=u["nome"], email=u["email"])


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@bp.get("/me")
def me():
    uid = session.get("user_id")
    u = usuario.buscar_por_id(uid) if uid else None
    if not u:
        return jsonify(erro="Não autenticado."), 401
    return jsonify(dict(u))

