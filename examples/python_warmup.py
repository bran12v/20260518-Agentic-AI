"""
Python warm-up - basic python syntax and concepts necessary for week 1
"""

# Type hinting

# basic addition function (no types)
def add_untyped(a, b):
    return a + b

# again basic addtion but with types so functions that use this know the contract 
def add(a: int, b: int):
    return a + b

# important syntax

# indentation = very important; colon ends the block header. No braces
"""
ticket = 
{
    "key": "value"
}

ticket["key"] = "value"

{
    "id": "TKT-10001",
    "title": "Invoice shows duplicate charge for April seats",
    "body": "Hi team - our April invoice (INV-2026-04-88421) shows two line items of $4,200 for the exact same seat pack. Pretty sure we only added 14 seats, not 28. Can someone look into this before our AP cutoff on the 25th? Happy to send screenshots.",
    "priority": "high",
    "status": "in_progress",
    "category": "billing",
    "tenant": "acme-corp",
    "customer_id": "CUS-10001",
    "assignee": "billing-team-lead",
    "channel": "email",
    "tags": ["invoice", "duplicate-charge", "q2-billing"],
    "created_at": "2026-04-18T14:22:31Z",
    "updated_at": "2026-04-21T09:47:15Z"
}
"""
# ticket priority = urgent -> finance-lead anything else -> general
# dict (dictionary) -> JSON (JavaScript Object Notation)
def route(ticket: dict) -> str:
    if ticket["priority"] == "urgent":
        return "finance-lead"
    return "general"

def escalate(ticket: dict) -> str:
    return f"escalated:{ticket['id']}"
    # "escalated:TK-10101"

def notify(ticket: dict) -> str:
    return f"notified:{ticket['id']}"

# duck typing -> the way a object is treated by python depends on its methods not necessarily its type

# double underscore -> dunder
def describe_size(thing) -> str:
    return f"{type(thing).__name__} of length {len(thing)}"



# public static void main(String[] args) {}
# This block only runs if we invoke the file directly. If the file is imported and used in another file this code will not run.
if __name__ == "__main__":
    # print(f"add(2,3)     =    {add(2,3)}")
    # print(f"add('foo','bar')     =    {add('foo','bar')}")

    # sample_ticket = {"id": "TKT-1", "priority": "asdasd"}
    # print(f"route(urgent)       = {route(sample_ticket)}")

    # handlers = [route, escalate, notify]
    # for handler in handlers:
    #     print(f"    {handler.__name__:<10} -> {handler(sample_ticket)}")

    # print(describe_size("hello"))
    # print(describe_size([1,2,3,4,5]))
    # print(describe_size({"a": "1", "b": "2", "c": "3"}))


    # fallback -> 'or' - returns the first "truthy" operand
    user_path = None
    default_path = "/etc/defaults"
    path = user_path or default_path # None or /etc/defaults
    # print(f"path = {path}")

    ticket = {"id": "TKT-1"}
    assignee = ticket.get("assignee") or "Unassigned"
    # print(f"assignee = {assignee}")

    # Mutable vs Immutable
    # Changable vs Unchangable -> list (mutable), tuple (immutable)
    # Dictionary (dict) -> keys must be immutable, values can be mutable.
    coord_to_label = {(0,0): "origin", (1,2): "northeast"}
    print(f"label at (0,0) = {coord_to_label[(0,0)]}")
    try: 
        broken = {[0,0]: "broken"}
    except TypeError as err:
        print(f"list as key fails: {err}")
