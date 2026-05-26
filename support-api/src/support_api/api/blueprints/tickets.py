from flask import Blueprint

# A Blueprint is a group of routes that we attach to the app later
bp = Blueprint("tickets", __name__)

# @bp.route("") - blueprints root. Root + a url_prefix + of /tickets + Empty string.
@bp.route("", methods=["GET"])
def list_tickets():
    return { "count": 0, "items": [] }