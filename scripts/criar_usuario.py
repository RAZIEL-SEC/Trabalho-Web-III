"""Cria um usuário da ONG direto no banco (não existe cadastro público).

Uso, da raiz do projeto, com o venv ativo e o banco no ar:
    python scripts/criar_usuario.py --nome "Raíssa Barreto" --email raissa@exemplo.org
"""
import argparse
import getpass
import os
import sys

# o .env fica em backend/, então rodamos a partir de lá
BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(BACKEND)
sys.path.insert(0, BACKEND)

from sqlalchemy import select  # noqa: E402

from app.core.security import gerar_hash  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--nome", required=True)
    p.add_argument("--email", required=True)
    args = p.parse_args()

    email = args.email.strip().lower()
    senha = getpass.getpass("Senha (mínimo 10 caracteres): ")
    if len(senha) < 10:
        sys.exit("Senha curta demais.")
    if senha != getpass.getpass("Repita a senha: "):
        sys.exit("As senhas não conferem.")

    with SessionLocal() as db:
        if db.scalar(select(Usuario).where(Usuario.email == email)):
            sys.exit("Já existe um usuário com esse e-mail.")
        usuario = Usuario(nome=args.nome.strip(), email=email, senha_hash=gerar_hash(senha))
        db.add(usuario)
        db.commit()
        print(f"Usuário criado: id={usuario.id}, email={usuario.email}")


if __name__ == "__main__":
    main()