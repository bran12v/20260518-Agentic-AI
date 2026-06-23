"""Supervisor node for handling the multi-agent support team."""

from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from support_agents.config import langchain_chat_model

SupervisorSpecialist = Literal["billing", "technical", "account"]

class RoutingDecision(BaseModel):
    """Supervisor's pick for which specialist should handle the ticket."""
    
    specialist: SupervisorSpecialist = Field(
        description="Which specialist team should handle this ticket."
    )
    reasoning: str = Field(
        max_length=240,
        description="One or two sentances explaining why this specialist."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="0.0-1.0. Below 0.6 the team_graph routes to human."
    )

SUPERVISOR_SYSTEM = (
    "You are the SUPERVISOR of a customer-support specialist team. Read the" \
    "incoming ticket and decide which specialist should handle it:\n\n" \
    "- billing: invoices, refunds, payment failures, subscription changes, and duplicate charges.\n"
    "- technical: integration errors, API failures, data pipeline issues, outages, and bug reports.\n" \
    "- account: user management, permissions, SSO, provisioning, and plan entitlements.\n\n" \
    "Assign exactly one specialist. If confidence is low (ambiguous ticket)," \
    "say so - the team_graph will route the ticket to a human queue when " \
    "your confidence is below 0.6."
)

async def classify_ticket(body: str, tenant: str | None = None) -> RoutingDecision:
    """Run the supervisor over a ticket body. Returns a typed 'RoutingDecision'."""
    model = langchain_chat_model().with_structured_output(RoutingDecision)
    user_prompt = f"Ticket body: \n\n{body}"
    if tenant:
        user_prompt = f"Tenant: {tenant}\n\n{user_prompt}"
    result = await model.ainvoke(
        [
            SystemMessage(content=SUPERVISOR_SYSTEM),
            HumanMessage(content=user_prompt)
        ]
    )
    assert isinstance(result, RoutingDecision)
    return result