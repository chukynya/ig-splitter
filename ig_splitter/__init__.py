from __future__ import annotations

from flask import Flask

from ig_splitter.config import BASE_DIR, MAX_UPLOAD_MB
from ig_splitter.web.routes import web_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
    app.register_blueprint(web_bp)
    return app
