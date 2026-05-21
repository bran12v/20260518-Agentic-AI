from pydantic import ValidationError
from support_api.domain import Ticket
from support_api.filters import load_tickets

raw = load_tickets()[0]

# Valid input returns a Ticket instance
ticket = Ticket.model_validate(raw)
print(f"Valid: id={ticket.id}   priority={ticket.priority}")
print(f"Type of the priority field: {type(ticket.priority).__name__}")

# Invalid input raising a structured error
try:
    Ticket.model_validate({**raw, "priority": "blocker"})
except ValidationError as err:
    print("Validation Error raised with:")
    for detail in err.errors():
        print(f"    loc={detail['loc']} type={detail['type']}   msg={detail['msg']}")