from support_api.routing_rules import DEFAULT_RULES, NoMatchingRule, TicketRouter

router = TicketRouter(DEFAULT_RULES)
broken = {"id": "TKT-Broken", "priority": "normal", "category": "completely-fake-category"}

try:
    router.route(broken)
except NoMatchingRule as e:
    print(f"Falling back: {e}")
    print(f"default queue = support-triage")