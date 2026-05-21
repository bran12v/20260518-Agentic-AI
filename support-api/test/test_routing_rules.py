import pytest

from support_api.routing_rules import (
    DEFAULT_RULES,
    NoMatchingRule,
    TicketRouter,
    RouteDecision
)

@pytest.fixture
def router() -> TicketRouter:
    return TicketRouter(DEFAULT_RULES)

def _ticket(**overrides):
    base = dict(
        id="TKT-99999", priority="normal", category="general",
        status="open", tenant="acme-corp",
    )
    # so this is actually not "or" its a dictionary merge
    #        original | wanted changes
    return base | overrides

def test_urgent_billing_goes_to_finance_lead(router):
    decision = router.route(_ticket(priority="urgent", category="billing"))
    assert isinstance(decision, RouteDecision)
    assert decision.queue == "finance-lead"

def test_unknown_category_raises(router):
    with pytest.raises(NoMatchingRule):
        router.route(_ticket(category="unknown-category"))


# parametrized decorator -> run multiple use case on a single function as separate tests
# no test case fails silently
@pytest.mark.parametrize(
    "category,expected_queue",
    [
        ("billing", "billing-team"),
        ("technical", "tier2-tech"),
        ("account", "account-team"),
        ("general", "support-triage")
    ]
)
def test_category_defaults(router, category, expected_queue):
    decision = router.route(_ticket(category=category))
    assert decision.queue == expected_queue