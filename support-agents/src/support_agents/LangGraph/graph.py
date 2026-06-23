"""LangGraph state machines for Triage."""

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from support_agents.config import langchain_chat_model
from support_agents.triage import TriageSuggestion
from support_agents.LangChain.triage_chain import build_classifier_chain

from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langgraph.graph import StateGraph, START, END
from support_agents.triage_tools import TRIAGE_TOOLS

from support_agents.graph_viz import draw_graphs

ESCALATION_THRESHOLD = 0.6

class TriageState(TypedDict, total=False):
    """State schema for the linear triage graph.
    
    'total=False' lets the nodes return partial updates - a node that only sets
    'suggestion' doesn't need to include/declare every other field.
    """
    body: str
    tenant: str | None
    tenant_summary: str
    suggestion: TriageSuggestion
    routed_team: str

class AgentState(TypedDict):
    """State schema for the cyclic tool-calling agent"""
    messages: Annotated[list[BaseMessage], add_messages]

AGENT_SYSTEM = (
    "You triage inbound customer-support tickets. You can call tools to gather "
    "context before classifying — but prefer fewer tool calls when the body "
    "alone is enough."
)
    
# Agent
def _agent_node_factory():
    """Bind tools at build time so every 'ainvoke' in the loop reuses the
    same bound model. Returns a node function closing over the bound model."""
    model_with_tools = langchain_chat_model().bind_tools(TRIAGE_TOOLS)

    async def _agent(state: AgentState) -> dict:
        response = await model_with_tools.ainvoke(state["messages"])
        return { "messages": [response] }
    
    return _agent

# Determining when to cycle back to the tools node
def _should_continue(state: AgentState) -> str:
    """Cycle back to tools if the last AIMessage requested more tool calls, else end."""
    last = state["messages"][-1]
    if getattr(last, "tools_calls", None): # boolean
        return "tools" # node
    return END # sentiel node

def build_agent_graph():
    """Cyclic graph: agent -> tools -> agent -> ... -> END"""
    graph = StateGraph(AgentState)
    graph.add_node("agent", _agent_node_factory())
    graph.add_node("tools", ToolNode(TRIAGE_TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent") # cyclical

    return graph.compile()


async def _enrich_with_tenant(state: TriageState) -> dict:
    """Optional context lookup. Skip gracefully when 'tenant' is missing."""
    tenant = state.get("tenant")
    if not tenant:
        return {"tenant_summary": "(no tenant provided)"}
    
    from support_agents import api_client

    recent = await api_client.list_tickets(tenant=tenant, limit=10)
    counts: dict[str, int] = {}
    for ticket in recent:
        counts[ticket["category"]] = counts.get(ticket["category"], 0) + 1
    summary_parts = [f"{count} {cat}" for cat, count in sorted(counts.items())]
    return {
        "tenant_summary": (
            f"Tenant {tenant} has {len(recent)} recent tickets "
            f"({', '.join(summary_parts) or 'none'})"
            # Ex1: Tenant acme-corp has 10 recent tickets (billing 4, finance 2, technical 4)
            # Ex2: Tenant acme-corp has 0 recent tickets (none)
        )
    }

async def _classify(state: TriageState) -> dict:
    chain = build_classifier_chain()
    # I could also provide the tenant summary here, if I made the necessary updates to guide
    # The prompt on what to do with that info.
    suggestion = await chain.ainvoke({"body": state["body"]})
    return { "suggestion": suggestion }

def _route_to_team(state: TriageState) -> dict:
    suggestion = state["suggestion"]
    team = suggestion.suggest_team or f"{suggestion.category}-team"
    return { "routed_team": team }

def _route_to_human(state: TriageState) -> dict:
    return {"routed_team": "human-queue"}

def _route_decision(state:TriageState) -> str:
    """Conditional edge: picks the next node from 'suggestion.confidence'."""
    suggestion = state.get("suggestion")
    if suggestion is None:
        return "route_to_human"
    return (
        "route_to_team"
        if suggestion.confidence >= ESCALATION_THRESHOLD
        else "route_to_human"
    )

def build_linear_graph():
    """Linear graph, no escalation yet. Compiled runnable ready to go."""
    graph = StateGraph(TriageState)
    # adding all my nodes to the graph
    graph.add_node("enrich_with_tenant", _enrich_with_tenant)
    graph.add_node("classify", _classify)
    graph.add_node("route_to_team", _route_to_team)
    graph.add_node("route_to_human", _route_to_human)

    # Edges
    graph.add_edge(START, "enrich_with_tenant")
    graph.add_edge("enrich_with_tenant", "classify")
    graph.add_conditional_edges(
        "classify",
        _route_decision,
        {"route_to_team": "route_to_team", "route_to_human": "route_to_human"}  # route["result of routing_decision str"]
    )
    graph.add_edge("route_to_team", END)
    graph.add_edge("route_to_human", END)
    return graph.compile()

def print_graphs() -> None:
    """Render both graphs via the shared 'draw_graphs' function from graph_viz.py"""
    draw_graphs([
        ("Linear graph", build_linear_graph),
        ("Agent graph", build_agent_graph)
    ])

async def main() -> None:
    import sys

    if "--draw" in sys.argv:
        print_graphs()
        return

    from support_agents.triage import TKT_10001_BODY

    print("\n--- Linear Graph ---")
    linear = build_linear_graph()
    results = await linear.ainvoke({"body": TKT_10001_BODY, "tenant": "acme-corp"})
    suggestion = results["suggestion"]
    print(f"routed_team:        {results["routed_team"]}")
    print(f"tenant_summary:     {results["tenant_summary"]}")
    print(f"classification:     {suggestion.category}/{suggestion.priority} "
          f"(confidence {suggestion.confidence:.2f})")
    
    print("\n--- Agent Graph ---")
    agent = build_agent_graph()
    agent_result = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=AGENT_SYSTEM),
                HumanMessage(content=f"Triage this ticket:\n\n{TKT_10001_BODY}\nAdd a score for the confidence that you have in your answer from 0.0 to 1.0.")
            ]
        }
    )
    final = agent_result["messages"][-1]
    print(f"Final reply: {final.content}")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())