import os
from pathlib import Path

from flask import Flask, g

from support_api.api.blueprints.tickets import bp as tickets_bp
from support_api.api.errors import register_error_handlers
from support_api.api.middleware import register_request_logging
from support_api.logging import configure_logging

_DEFAULT_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "tickets.db"
)

# Entrypoint
def create_app(db_path: Path | str | None = None) -> Flask:
    # makes sure that Flasks inital startup events go thru struct log
    configure_logging()

    # __name__ tells Flask where to anchor static/template paths
    app = Flask(__name__)

    app.config["DB_PATH"] = str(
        db_path or os.environ.get("DB_PATH") or _DEFAULT_DB_PATH
    )

    # Mount the blueprint at /tickets.
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    register_error_handlers(app)
    register_request_logging(app)

    @app.teardown_appcontext
    def _close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # root
    @app.route("/", methods=["GET"])
    def index() -> dict[str, str]:
        return {"service": "support-api", "version": "1.0.0"}

    return app