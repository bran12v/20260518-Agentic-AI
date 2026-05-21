from support_api.filters import count_by_category, filter_by_priority, filter_by_tenant

def test_filter_by_priority_urgent_subset(seed_tickets):
    urgent = filter_by_priority(seed_tickets, "urgent")
    assert all(ticket["priority"] == "urgent" for ticket in urgent)

