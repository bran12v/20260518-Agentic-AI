from datetime import datetime, timezone

from flask import Blueprint, request, g, current_app
import json
import structlog
from support_api.api.errors import TicketNotFound
from support_api.domain import TicketCreate
from support_api.filters import filter_by_priority, filter_by_tenant, load_tickets
from support_api.logging import configure_logging
from support_api.storage import queries

# A Blueprint is a group of routes that we attach to the app later
bp = Blueprint("tickets", __name__)

log = structlog.get_logger(__name__)

def _db():
    if "db" not in g:
        from support_api.storage import connect
        g.db = connect(current_app.config["DB_PATH"])
        log.info("connection_estabilished", db=g.db)
    return g.db # db connection

# @bp.route("") - blueprints root. Root + a url_prefix + of /tickets + Empty string.
@bp.route("", methods=["GET"])
def list_tickets():
    """List all tickets in database."""
    tickets = queries.list_tickets(
        _db(),
        priority=request.args.get("priority"),
        tenant=request.args.get("tenant"),
        status=request.args.get("status"),
        limit=int(request.args.get("limit", 100)),
    )
    return { "count": len(tickets), "items": tickets }

# http://localhost:5000         /tickets                /TKT-10001
#           root                url_prefix               ticket_id
@bp.route("/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id: str):
    """Scan for a ticket."""
    ticket = queries.get_ticket(_db(), ticket_id)
    if ticket is None:
        raise TicketNotFound(ticket_id)
    return ticket

# POST
@bp.route("", methods=["POST"])
def create_ticket():
    data = TicketCreate.model_validate(request.get_json(silent=True) or {})
    conn = _db()
    count = conn.execute("SELECT COUNT(*) AS n FROM tickets").fetchone()["n"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    new_ticket = {
        **data.model_dump(),
        "id": f"TKT-{10001 + count:05d}",
        "created_at": now,
        "updated_at": now,
    }
    queries.insert_ticket(conn, new_ticket)
    conn.commit()
    return new_ticket, 201 # created