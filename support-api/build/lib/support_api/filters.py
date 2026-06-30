"""Pure filter, transform and aggregate functions over ticket dicts"""

import json
from pathlib import Path
import re
from typing import Callable

# Path(__file__).resolve()  = C:\Users\<user>\Desktop\support-platform\support-api\src\support_api\filters.py
# _DATA_DIR                 = C:\Users\<user>\Desktop\support-platform\support-api\data
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def load_tickets(path: Path | None = None) -> list[dict]:
    """Load the seed tickets.json into memory as a list of dicts"""
    target = path or (_DATA_DIR / "tickets.json")
    # print(f"target = {target}")
    with target.open(encoding="utf-8") as fn:
        return json.load(fn)
    
def filter_by_priority(tickets: list[dict], priority: str):
    """Returns tickets whose priority matches. Case-insensitive"""
    desired_priority = priority.lower()
    return [ticket for ticket in tickets if ticket.get("priority", "").lower() == desired_priority]

def filter_by_tenant(tickets, tenant):
    """Return tickets scoped to one tenant."""
    desired_tenant = tenant
    return [ticket for ticket in tickets if ticket.get("tenant") == desired_tenant]

def count_by_category(tickets):
    """Bucket the tickets by category. All values sum to len(tickets)"""
    counts = {}
    for ticket in tickets:
        key = ticket.get("category", "unknown")
        counts[key] = counts.get(key, 0) + 1 # counts[key]++
    return counts

def most_recent(tickets, n=5):
    """return the n most recently created tickets"""
    return sorted(tickets, key=lambda t: t["created_at"], reverse=True)[:n]

def format_ticket_row(ticket):
    """return a one-line human-readable summary of a ticket"""
    short_title = ticket["title"]
    if len(short_title) > 50:
        short_title = short_title[:47] + "..."
    return (
        f"{ticket["id"]:<10}"
        f"{ticket["priority"]:<8}"
        f"{ticket["status"]:<20}"
        f"{short_title}"
    )

def extract_error_codes(text):
    """Find HTTP-style status codes (4xx / 5xx) mentioned in text.
    
    Return a list of strings. Deduplicated, order-preserving.
    """
    # \b is a word boundary. (only get words/characters that match exactly what is given, standalone). [45] matches to 4 or 5. \d{2} matches two digits.
    pattern = r"\b[45]\d{2}\b"
                #4 or 5 and 2 digits after
    seen = []
    for match in re.findall(pattern, text):
        if match not in seen:
            seen.append(match)
    return seen

def has_tenant_admin_request(body):
    """True if the body mentions tenant-admin / owner / admin operations"""
    pattern = r"(?i)\b(tenant admin|admin access|owner role)\b"
    return re.search(pattern, body) is not None


#               Function(params) -> return type # apply(list[dict]) -> list[dict]:
def matches(predicate: Callable[[dict], bool]) -> Callable[[list[dict]], list[dict]]: 
    """Return a filter function scoped to one predicate
    
    """
    def apply(tickets: list[dict]) -> list[dict]:
        return [t for t in tickets if predicate(t)]
    return apply
    

if __name__ == "__main__":
    tickets = load_tickets()

    # lambda (function), one-off throwaway function
    # for t in tickets: t["priority"] ==== lambda t: t["priority"]
    is_urgent = matches(lambda t: t["priority"] == "urgent")
    is_billing = matches(lambda t: t["category"] == "billing")
    is_high_billing = matches(lambda t: t["priority"] == "high" and t["category"] == "billing")

    print(f"Urgent: {len(is_urgent(tickets))}")
    print(f"Billing: {len(is_billing(tickets))}")
    print(f"High Priority Billing: {len(is_high_billing(tickets))}")

    # print("\n=== Tickets mentioning admin access ===")
    # admin_tickets = [t for t in tickets if has_tenant_admin_request(t.get("body", ""))]
    # print(f"Count: {len(admin_tickets)}")
    # for t in admin_tickets[:3]:
    #     print(f"    {t['id']}: {t['title']}")


    # print("\n=== Tickets with error codes mentioned ===")
    # for t in tickets:
    #     codes = extract_error_codes(t.get("body"))
    #     if codes:
    #         print(f"{t['id']}   codes={codes}   title={t['title'][:40]}")



    # print("\n=== 5 most recent tickets ===")
    # for t in most_recent(tickets, 5):
    #     print(format_ticket_row(t)) 


    # # function chaining
    # print("\n=== Top 3 urgent tickets, newest first ===")
    # for t in most_recent(filter_by_priority(tickets, "urgent"), 3):
    #     print(format_ticket_row(t))

    

    # print(f"Category counts: {count_by_category(tickets)}")

    urgent = filter_by_priority(tickets, "urgent")
    # print(f"Urgent: {len(urgent)}")

    acme = filter_by_tenant(tickets, "acme-corp")
    # print(f"acme-corp tickets: {len(acme)}")

    # comprehensions (one liner)
    # easy way of extracting existing information from collections in one line.

    # --- List Comprehension: urgent tickets ---
    # [expression for item in iterable if condition]
    # creates a new list
    # we want to list all titles of urgent tickets 
    urgent_titles = [ticket["title"] for ticket in tickets if ticket["priority"] == "urgent"]
    # print(f"Urgent ticket count: {len(urgent_titles)}")

    # --- Set Comprehension: unique tenants
    # {expression for item in iterable}
    tenants = {ticket["tenant"] for ticket in tickets}
    # print(f"Tenants: {sorted(tenants)}")

    # --- Dict Comprehension: id -> title lookup table ---
    # {key_expr: value_expr for item in iterable}
    title_by_id = {ticket["id"]: ticket["title"] for ticket in tickets} # dict of all the tickets {id: title}
    # print(f"Lookup TKT-10002: {title_by_id.get("TKT-10002", "Not Found")}") # one specific ticket title

    # --- Nested Comprehension: all unique tags across all tickets ---
    all_tags = {tag for ticket in tickets for tag in ticket.get("tags", [])}
    # print(f"Distinct tag count: {len(all_tags)}")
    # print(f"Top 5 tags: {sorted(all_tags)[:5]}")

    

    # print(type(tickets))
    # print(len(tickets))
    # print(type(tickets[0]))
    # print(json.dumps(tickets[0], indent=2))

    # Square-bracket access - raises a KeyError if the key is missing
    first = tickets[0]
    id = first["id"] #"TKT-10001"
    title = first["title"]
    # print(f"{id}: {title}")

    # .get() / you can give a default variable (fallback) for if the key is missing 
    assignee = first.get("assignee") or "UNASSIGNED"
    # print(f"Assignee: {assignee}")

    # similar to JS, Tuple unpacking
    ticket_id, priority, status = first["id"], first["priority"], first["status"]
    # print(f"{ticket_id}, {priority}, {status}")

    # membership - "in" checks keys dicts, values for lists
    has_tags = "tags" in first 
    # print(f"Has tags field: {has_tags}")

    # Sets - unordered list of unique values. 
    priorities = set()
    for ticket in tickets:
        priorities.add(ticket["priority"])
    # print(f"Priorities: {sorted(priorities)}")



