import os

from flask import Flask, send_from_directory

from config import Config, close_db, init_db
from models import projeto
from routes import doacoes, projetos, usuarios


def create_app(test_config=None):
    app = Flask(
        __name__,
        static_folder=os.path.join(Config.FRONTEND_DIR, "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    for mod in (usuarios, projetos, doacoes):
        app.register_blueprint(mod.bp)

    templates = os.path.join(app.config["FRONTEND_DIR"], "templates")

    @app.get("/")
    def home():
        return send_from_directory(templates, "index.html")

    @app.get("/<page>.html")
    def pagina(page):
        return send_from_directory(templates, f"{page}.html")

    with app.app_context():
        init_db()
        projeto.popular_exemplo()

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
