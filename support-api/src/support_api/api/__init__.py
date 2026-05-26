from flask import Flask

from support_api.api.blueprints.tickets import bp as tickets_bp
from support_api.logging import configure_logging

def create_app():
    # makes sure that Flasks inital startup events go thru struct log
    configure_logging()

    # __name__ tells Flask where to anchor static/template paths
    app = Flask(__name__)

    # Mount the blueprint at /tickets.
    app.register_blueprint(tickets_bp, url_prefix="/tickets")

    # root
    @app.route("/", methods=["GET"])
    def index() -> dict[str, str]:
        return {"service": "support-api", "version": "1.0.0"}

    return app