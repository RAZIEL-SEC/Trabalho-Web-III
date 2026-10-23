from config import get_db


def criar(usuario_id, projeto_id, valor):
    db = get_db()
    cur = db.execute(
        "INSERT INTO doacoes (usuario_id, projeto_id, valor) VALUES (?, ?, ?)",
        (usuario_id, projeto_id, valor),
    )
    db.commit()
    return cur.lastrowid


def listar_do_usuario(usuario_id):
    return [dict(r) for r in get_db().execute(
        """SELECT d.id, d.valor, d.criado_em, p.titulo AS projeto
           FROM doacoes d JOIN projetos p ON p.id = d.projeto_id
           WHERE d.usuario_id = ? ORDER BY d.id DESC""",
        (usuario_id,),
    )]


def resumo(usuario_id):
    row = get_db().execute(
        "SELECT COUNT(*) AS qtd, COALESCE(SUM(valor), 0) AS total "
        "FROM doacoes WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()
    geral = get_db().execute(
        "SELECT COALESCE(SUM(valor), 0) FROM doacoes"
    ).fetchone()[0]
    return {"minhas_doacoes": row["qtd"], "meu_total": row["total"], "total_geral": geral}
