from datetime import datetime, timezone

from flask import Blueprint, request
import json
from support_api.api.errors import TicketNotFound
from support_api.domain import TicketCreate
from support_api.filters import filter_by_priority, filter_by_tenant, load_tickets

# A Blueprint is a group of routes that we attach to the app later
bp = Blueprint("tickets", __name__)

# @bp.route("") - blueprints root. Root + a url_prefix + of /tickets + Empty string.
@bp.route("", methods=["GET"])
def list_tickets():
    """List all tickets in database."""
    # stat with seeding tickets; later this will become a SQL query (db will be seeded elsewhere)
    tickets = load_tickets()

    priority = request.args.get("priority")
    print(f"{json.dumps(request.args)}") 
    if priority:
        tickets = filter_by_priority(tickets, priority)

    tenant = request.args.get("tenant")
    if tenant:
        tickets = filter_by_tenant(tickets, tenant)

    return { "count": len(tickets), "items": tickets }

# http://localhost:5000         /tickets                /TKT-10001
#           root                url_prefix               ticket_id
@bp.route("/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id: str):
    """Scan for a ticket."""
    # linear scan for today - going to be replaced with SQL Query
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            # Happy Path
            return ticket
        
    # Failure Path
    # raise for exceptions, return for everything else (text, dict, etc)
    raise TicketNotFound(ticket_id)


# POST
@bp.route("", methods=["POST"])
def create_ticket():
    # silent=True -> None on a bad body `or {}` -> Pydantic will report ALL fields as missing
    # rather than just "body cant be None"
    data = TicketCreate.model_validate(request.get_json(silent=True) or {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    # 2026-05-27T10:50:00Z - current timestamp
    existing = load_tickets()
    return (
        {
            **data.model_dump(), # spread validated fields
            "id": f"TKT-{10001 + len(existing):05d}",
            "created_at": now,
            "updated_at": now,
        },
        201, # 201 created
    )