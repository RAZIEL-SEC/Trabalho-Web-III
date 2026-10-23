from flask import Blueprint, jsonify, request, session

from models import projeto

bp = Blueprint("projetos", __name__, url_prefix="/api/projetos")


@bp.get("")
def listar():
    return jsonify(projeto.listar())


@bp.post("")
def criar():
    if not session.get("user_id"):
        return jsonify(erro="Faça login primeiro."), 401
    d = request.get_json(silent=True) or {}
    titulo = (d.get("titulo") or "").strip()
    if not titulo:
        return jsonify(erro="Título obrigatório."), 400
    try:
        meta = float(d.get("meta") or 0)
    except ValueError:
        return jsonify(erro="Meta inválida."), 400
    pid = projeto.criar(titulo, (d.get("descricao") or "").strip(), meta)
    return jsonify(id=pid), 201

