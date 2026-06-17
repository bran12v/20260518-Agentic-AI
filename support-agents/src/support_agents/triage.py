""" Pydantic-typed triage of a raw support ticket body.

Use schema enforced structure output so the LLM's response fits directly into the typed domain.
"""
from support_agents.config import openai_client, MODEL

from support_agents.schemas import TriageSuggestion, Category, Priority

__all__ = ["Category", "Priority", "TriageSuggestion", "triage", "TKT_10001_BODY"]

def triage(body: str) -> TriageSuggestion:
    response = openai_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a triage assistant for a customer-support platform."
                "Assign priority by impact, not tone:"
                "- urgent: active outage, data loss, sercurity incident, or full blocked work. Active critical issue, currently occuring."
                "- high: significant problem with real business/financial concequences/impacts in the near-term"
                "- normal: a routine issue, or question without a deadline"
                "- low: praise, feedback, or a minor non-blocking issue.",
            },
            { "role": "user", "content": f"Triage the inbound ticket: \n\n{body}"}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "TriageSuggestion",
                "schema": TriageSuggestion.model_json_schema(),
                "strict": True
            },
        },
    )
    return TriageSuggestion.model_validate_json(response.choices[0].message.content)

TKT_10001_BODY = (
    "Hi team - our April invoice (INV-2026-04-88421) shows two line items of $4,200 for the exact same seat pack. Pretty sure we only added 14 seats, not 28. Can someone look into this before our AP cutoff on the 25th? Happy to send screenshots."
)

def main() -> None:
    result = triage(TKT_10001_BODY)
    print(f"category:     {result.category}")
    print(f"priority:     {result.priority}")
    print(f"summary:      {result.summary}")
    print(f"suggest_team: {result.suggest_team}")
    print(f"\n (as a dict, ready for downstream code): \n{result.model_dump_json(indent=2)}")

if __name__ == "__main__":
    main()