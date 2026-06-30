
from dataclasses import dataclass
from typing import Any

DEFAULT_RULES: list[dict[str, Any]] = [
    {
        "name": "urgent-billing-to-finance-lead",
        "queue": "finance-lead",
        "when": {"priority": "urgent", "category": "billing"},
    },
    {"name": "technical-anything-to-tier2", "queue": "tier2-tech", "when": {"category": "technical"}},
    {"name": "billing-default", "queue": "billing-team", "when": {"category": "billing"}},
    {"name": "account-default", "queue": "account-team", "when": {"category": "account"}},
    {"name": "general-default", "queue": "support-triage", "when": {"category": "general"}},
]

@dataclass(frozen=True)
class RouteDecision:
    """The router's answer for a single ticket."""

    queue: str = ""
    rule_name: str = ""
    confidence: float = 0.0 # this a value between 0.0 and 1.0

# Custom Exception
class NoMatchingRule(Exception):
    """Raised when no rules are matched. Caller should apply a default queue."""

class TicketRouter:
    """ Route tickets to team queues using ordered match rules.

    The first matching rule wins. Rules are dicts with:
        name - human-readable id
        queue - target queue string
        when - mapping of ticket field -> expected value or tuple of values
    """
    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self._rules = rules
    
    def route(self, ticket: dict[str, Any]) -> RouteDecision:
        for rule in self._rules:
            if self._rule_matches(rule, ticket):
                return RouteDecision(
                    queue=rule["queue"], rule_name=rule["name"], confidence=1.0
                )
        raise NoMatchingRule(
            f"no rule fired for ticket {ticket.get('id', '<no-id>')}"
        )

    # class with only logic, and no self references, we can make it static
    @staticmethod
    def _rule_matches(rule: dict[str, Any], ticket: dict[str, Any]) -> bool:
        """Determine if a rule is within the list of rules"""
           # key,   value
        for key, value in rule["when"].items():
            actual = ticket.get(key)
            if isinstance(value, tuple):
                if actual is not value:
                    return False
            elif actual != value:
                return False
        return True

    # NO SUCH THING AS ACCESS MODIFIERS IN PYTHON, at least not really. (only conventions)
    # __rules -> name mangles to _TicketRouter__rules,
    # if I were to set self.__rules later on to a different value it would instead set a new field not the original.

if __name__ == "__main__":
    from support_api.filters import load_tickets
    router = TicketRouter(DEFAULT_RULES)
    for ticket in load_tickets()[:10]:
        decision = router.route(ticket)
        print(f"{ticket['id']}  -> {decision.queue} ({decision.rule_name})")