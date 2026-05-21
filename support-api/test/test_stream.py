from support_api.stream import take, where

def test_where_filters_by_predicate(seed_tickets):
    urgent = list(where(seed_tickets, lambda t: t["priority"] == "urgent"))
    assert all(t["priority"] == "urgent" for t in urgent)

    # kubernetes