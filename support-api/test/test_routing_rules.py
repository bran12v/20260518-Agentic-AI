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