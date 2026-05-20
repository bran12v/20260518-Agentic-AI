from support_api.routing_rules import RouteDecision

d = RouteDecision(rule_name="billing-default", confidence=1.0, queue="billing-team")

print(d) # __repr__

# __eq__
print(d == RouteDecision("billing-team", "billing-default", 1.0))

# frozen=True prevents mutation
try:
    d.queue = "other"
except Exception as e:
    print(type(e).__name__, e)

#__hash__ - key