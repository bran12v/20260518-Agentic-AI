import pytest
from support_api.domain import Ticket


def test_every_seeded_ticket_validates(seed_tickets):
    """Catches drift if anyone hand-edits tickets.json wrongly."""
    for raw in seed_tickets:
        Ticket.model_validate(raw)