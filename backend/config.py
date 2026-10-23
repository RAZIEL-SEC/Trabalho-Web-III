import os
import sqlite3

from flask import current_app, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-troque-em-producao")
    DATABASE = os.environ.get("DATABASE", os.path.join(ROOT_DIR, "ong.db"))
    SCHEMA = os.path.join(ROOT_DIR, "database", "schema.sql")
    FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def get_db():
    """Uma conexão SQLite por requisição."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with open(current_app.config["SCHEMA"], encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
