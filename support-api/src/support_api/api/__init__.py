import os
from pathlib import Path

from flask import Flask, g

from support_api.api.blueprints.tickets import bp as tickets_bp
from support_api.api.errors import register_error_handlers
from support_api.api.middleware import register_request_logging
from support_api.logging import configure_logging
from support_api.api.blueprints.health import bp as health_bp

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_DEFAULT_DATABASE_URL = "postgresql://support:support_dev@db:5432/support"

# Entrypoint
def create_app(database_url: Path | str | None = None) -> Flask:
    # makes sure that Flasks inital startup events go thru struct log
    configure_logging()

    # __name__ tells Flask where to anchor static/template paths
    app = Flask(__name__)

    app.config["DATABASE_URL"] = str(
        database_url or os.environ.get("DATABASE_URL") or _DEFAULT_DATABASE_URL
    )

    # Mount the blueprint at /tickets.
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(health_bp)
    register_error_handlers(app)
    register_request_logging(app)

    Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per minute"],
        storage_uri="memory://",
    )

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