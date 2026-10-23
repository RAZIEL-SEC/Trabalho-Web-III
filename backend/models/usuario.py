from werkzeug.security import check_password_hash, generate_password_hash

from config import get_db


def criar(nome, email, senha):
    db = get_db()
    cur = db.execute(
        "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
        (nome, email.lower(), generate_password_hash(senha)),
    )
    db.commit()
    return cur.lastrowid


def buscar_por_email(email):
    return get_db().execute(
        "SELECT * FROM usuarios WHERE email = ?", (email.lower(),)
    ).fetchone()


def buscar_por_id(user_id):
    return get_db().execute(
        "SELECT id, nome, email FROM usuarios WHERE id = ?", (user_id,)
    ).fetchone()


def autenticar(email, senha):
    u = buscar_por_email(email)
    if u and check_password_hash(u["senha_hash"], senha):
        return u
    return None

