from config import get_db


def listar():
    return [dict(r) for r in get_db().execute(
        """SELECT p.id, p.titulo, p.descricao, p.meta,
                  COALESCE(SUM(d.valor), 0) AS arrecadado
           FROM projetos p LEFT JOIN doacoes d ON d.projeto_id = p.id
           GROUP BY p.id ORDER BY p.id DESC"""
    )]


def existe(projeto_id):
    return get_db().execute(
        "SELECT 1 FROM projetos WHERE id = ?", (projeto_id,)
    ).fetchone() is not None


def criar(titulo, descricao="", meta=0):
    db = get_db()
    cur = db.execute(
        "INSERT INTO projetos (titulo, descricao, meta) VALUES (?, ?, ?)",
        (titulo, descricao, meta),
    )
    db.commit()
    return cur.lastrowid


def popular_exemplo():
    """Insere projetos de exemplo se a tabela estiver vazia."""
    db = get_db()
    if db.execute("SELECT COUNT(*) FROM projetos").fetchone()[0] == 0:
        criar("Cesta Básica Solidária", "Distribuição mensal de cestas básicas.", 5000)
        criar("Reforço Escolar", "Aulas de reforço para crianças da comunidade.", 3000)

