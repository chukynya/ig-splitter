from __future__ import annotations

from flask import Flask

from ig_splitter.config import BASE_DIR
from ig_splitter.web.routes import web_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.register_blueprint(web_bp)
    return app
