from flask import Blueprint, jsonify, request, session

from models import doacao, projeto

bp = Blueprint("doacoes", __name__, url_prefix="/api/doacoes")


def _uid():
    return session.get("user_id")


@bp.get("")
def minhas():
    if not _uid():
        return jsonify(erro="Faça login primeiro."), 401
    return jsonify(doacao.listar_do_usuario(_uid()))


@bp.post("")
def doar():
    if not _uid():
        return jsonify(erro="Faça login primeiro."), 401
    d = request.get_json(silent=True) or {}
    try:
        projeto_id, valor = int(d.get("projeto_id")), float(d.get("valor"))
    except (TypeError, ValueError):
        return jsonify(erro="Projeto e valor inválidos."), 400
    if valor <= 0 or not projeto.existe(projeto_id):
        return jsonify(erro="Valor deve ser positivo e projeto existente."), 400
    return jsonify(id=doacao.criar(_uid(), projeto_id, valor)), 201


@bp.get("/resumo")
def resumo():
    if not _uid():
        return jsonify(erro="Faça login primeiro."), 401
    return jsonify(doacao.resumo(_uid()))

