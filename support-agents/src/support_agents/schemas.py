from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["billing", "technical", "account", "general"]
Priority = Literal["urgent", "high", "normal", "low"]

class TriageSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category
    priority: Priority
    summary: str = Field(max_length=120, description="One-sentance plain summary")
    suggest_team: str | None = Field(
        description="Team name in kebab-case, e.g. 'billing-team'. None if unclear"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How sure the model is, 0.0 to 1.0. Below 0.6 the graph routes to" \
            "a human queue instead of automated team."
        )
    )