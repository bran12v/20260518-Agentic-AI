from support_agents.triage import triage, TriageSuggestion

"""Golden Set - 3 labeled tickets with documented results. In production,
this would live in your main repo and run on every CI pipeline run for each
prompt change.
Each entry: ticket body + expected result (category, priority)"""

GOLDEN = [
    {
        "id": "TKT-10001",
        "body": "Hi team - our April invoice (INV-2026-04-88421) shows two line items of $4,200 for the exact same seat pack. Pretty sure we only added 14 seats, not 28. Can someone look into this before our AP cutoff on the 25th? Happy to send screenshots.",
        "expected": ("billing", "high")
    },
    {
        "id": "TKT-10002",
        "body": "We're hitting 429 Too Many Requests on POST /api/v2/exports even though we're well under the documented 60 rpm limit. Retry-After header says 47 seconds. This started around 2026-04-19 08:00 UTC. Running from our us-east prod cluster. Example request id: req_8f3d2a1c9e.",
        "expected": ("technical", "urgent")
    },
    {
        "id": "TKT-10003",
        "body": "Hi - new admin here. I've figured out how to run a one-off export but I need it to run every Monday at 6am and drop into our SFTP. Is there a docs page on this? Couldn't find one that matched the current UI. Thanks!",
        "expected": ("technical", "normal")
    },
]

score = 0
for case in GOLDEN:
    pred = triage(case["body"])
    got = (pred.category, pred.priority) # ("general", "low")
    passed = got == case["expected"]
    if passed:
        score += 1
    marker = "[PASS]" if passed else "[FAIL]"
    print(f"    {marker} {case['id']}: got {got}, expected {case['expected']}")

print(f"\nscore:    {score}/{len(GOLDEN)}")
if score < len(GOLDEN):
    print("REGRESSION - CI would reject this prompt change.")