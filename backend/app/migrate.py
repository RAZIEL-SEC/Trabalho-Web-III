"""Aplica migrações SQL idempotentes antes de iniciar a API."""

from pathlib import Path

from app.db.session import engine


def main() -> None:
    pasta = Path(__file__).resolve().parents[2] / "database" / "migrations"
    migrations = sorted(pasta.glob("*.sql"))
    with engine.begin() as connection:
        for migration in migrations:
            sql = migration.read_text(encoding="utf-8")
            # Os scripts devem ser transacionais e seguros para reexecução.
            connection.exec_driver_sql(sql)


if __name__ == "__main__":
    main()
