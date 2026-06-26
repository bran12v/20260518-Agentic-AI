"""Hierarchical multi-agent routing."""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from support_agents.config import langchain_chat_model
from support_agents.LangGraph.specialists import (
    build_account_specialist,
    build_billing_specialist,
    build_technical_specialist
)

Tier = Literal["tier1_direct", "tier2_escalate"]
Tier1Target = Literal["billing", "account"]

class TierRouting(BaseModel):
    """Tier-1 supervisor's route decision."""

    tier: Tier = Field(description="Which tier should handle this ticket.") # main binary decision
    tier1_target: Tier1Target | None = Field( # sub decision (tier1)
        default=None,
        description="If tier=tier1_direct, which tier-1 team: billing or account."
    )
    escalation_reason: str | None = Field(
        default=None,
        max_length=240,
        description=(
            "If tier=tier2_escalate, a one sentance reason. Refereneced by the" \
            "tier-2 senior-engineer router."
        )
    )

TIER1_SYSTEM = (
    "You are the TIER-1 supervisor for a customer-support org.\n\n"
    "- tier1_direct: the tier-1 team can close this ticket. Billing or account "
    "  questions with clear scope and no hint of technical complexity.\n"
    "- tier2_escalate: escalate to tier-2 technical. Integration errors, API "
    "  failures, outages, complex bugs, or anything where the customer is "
    "  reporting that the product itself is broken.\n\n"
    "Be biased toward tier1_direct when the scope is clearly bounded — over-"
    "escalation is expensive."
)

async def classify_tier(body: str, tenant: str | None = None) -> TierRouting:
    """Tier-1 supervisor classification. LLM decision, no tools."""
    model = langchain_chat_model().with_structured_output(TierRouting)
    user_prompt = f"Ticket body: \n\n{body}"
    if tenant:
        user_prompt = f"Tenant: {tenant}\n\n{user_prompt}"
    result = await model.ainvoke(
        [SystemMessage(content=TIER1_SYSTEM), HumanMessage(content=user_prompt)]
    )
    assert isinstance(result, TierRouting)
    return result

class HierState(TypedDict, total=False):
    """State graph object for our LangGraph agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    body: str
    tenant: str | None
    routing: TierRouting

SENIOR_ENGINEER_SYSTEM = (
    "You are the SENIOR ENGINEER on the tier-2 technical team. You handle "
    "incidents that the general technical specialist would need to escalate: "
    "multi-tenant outages, data-loss events, anything involving on-call. "
    "Be succinct. If the situation is not in fact senior-grade, say so."
)

def _senior_engineer_node_factory():
    from langgraph.prebuilt import create_react_agent
    from support_agents.triage_tools import TRIAGE_TOOLS

    agent = create_react_agent(
        langchain_chat_model(), TRIAGE_TOOLS, prompt=SENIOR_ENGINEER_SYSTEM
    )

    async def _node(state: HierState) -> dict:
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": [result["messages"][-1]]}
    
    return _node

def _is_senior_case(reason: str | None) -> bool:
    """Decide whether a tier-2 escalation warrants the senior engineer.
    
    Simple keyword heuristic - a real system might use a classifier or rules."""
    if not reason:
        return False
    senior_signal = ("outage", "data loss", "incident", "production down", "critical")
    return any(signal in reason.lower() for signal in senior_signal)

async def _tier1_supervisor_node(state: HierState) -> dict:
    routing = await classify_tier(state["body"], state.get("tenant"))
    note = AIMessage(
        content=(
            f"[tier-1] tier={routing.tier} "
            f"{('target=' + routing.tier1_target) if routing.tier1_target else ''} "
            f"{('reason=' + routing.escalation_reason) if routing.escalation_reason else ''}"
        )
    )
    return {"routing": routing, "messages": [note]}
    
def _make_specialist_wrapper(builder):
    agent = builder()

    async def _node(state: HierState) -> dict:
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": [result["messages"][-1]]}
    
    return _node

def _pick_tier1_path(state: HierState) -> str:
    """First conditional edge: tier-1 direct vs tier-2 escalate."""
    routing = state.get("routing")
    if routing is None:
        return "tier2_general"
    if routing.tier == "tier1_direct":
        return routing.tier1_target or "billing" # default in case of tier1_target not being set.
    return "tier2_senior" if _is_senior_case(routing.escalation_reason) else "tier2_general"

def build_hierarchical_graph():
    """Compile the hierarchical support team graph."""
    graph = StateGraph(HierState)
    graph.add_node("tier1_supervisor", _tier1_supervisor_node)
    graph.add_node("billing", _make_specialist_wrapper(build_billing_specialist))
    graph.add_node("account", _make_specialist_wrapper(build_account_specialist))
    graph.add_node("tier2_general", _make_specialist_wrapper(build_technical_specialist))
    graph.add_node("tier2_senior", _senior_engineer_node_factory())

    graph.add_edge(START, "tier1_supervisor")
    graph.add_conditional_edges(
        "tier1_supervisor",
        _pick_tier1_path,
        {
            "billing": "billing",
            "account": "account",
            "tier2_general": "tier2_general",
            "tier2_senior": "tier2_senior"
        }
    )
    for leaf in ("billing", "account", "tier2_general", "tier2_senior"):
        graph.add_edge(leaf, END)
    return graph.compile()

async def demo_route() -> None:
    """End to end test for the hierarchical graph"""
    tickets = [
        (
            "clear billing question",
            "I was double-charged on my latest invoice — two identical line "
            "items for the same seat. Can you explain and refund the extra?",
        ),
        (
            "production incident",
            "(TKT-10021) Your API has returned 500s for our ENTIRE org for 20 minutes. "
            "Production is hard down — a full outage affecting all our users.",
        ),
    ]
    graph = build_hierarchical_graph()
    for label, body in tickets:
        print(f"\n==ticket: {label} ===")
        result = await graph.ainvoke(
            {"body": body, "messages": [HumanMessage(content=body)]}
        )
        for msg in result["messages"]:
            print(f"    [{type(msg).__name__} {msg.content}]")

def main() -> None:
    """Argv-driven dispatcher for running our hierarchical state graph"""

    import asyncio
    import sys
    flags = {
        "--route": demo_route
    }
    for flag, fn in flags.items():
        if flag in sys.argv:
            asyncio.run(fn())
            return

if __name__ == "__main__":
    main()