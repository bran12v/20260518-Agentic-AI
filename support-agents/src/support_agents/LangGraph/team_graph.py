"""Multi-agent graph.

Wires the supervisor and the three specialists into one StateGraph:

START -> supervisor -> [billing | technical | account | human_queue] -> END
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from support_agents.LangGraph.supervisor import RoutingDecision, classify_ticket
from support_agents.LangGraph.specialists import SPECIALIST_BUILDERS

SUPERVISOR_CONFIDENCE_MIN = 0.6

class TeamState(TypedDict, total=False):
    """State for the multi-agent team graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    body: str
    tenant: str | None
    routing: RoutingDecision

async def _supervisor_node(state: TeamState) -> dict:
    routing = await classify_ticket(state["body"], state.get("tenant"))
    note = AIMessage(
        content=(
            f"[supervisor] routed to {routing.specialist} "
            f"(confidence {routing.confidence:.2f}): {routing.reasoning}"
        )
    )
    return {"routing": routing, "messages": [note]}

def _make_specialist_node(specialist_name: str):
    """Wrap a compiled specialist graph as a single parent-graph node."""
    agent = SPECIALIST_BUILDERS[specialist_name]()

    async def _node(state: TeamState) -> dict:
        result = await agent.ainvoke({"messages": state["messages"]})
        return {"messages": result["messages"][-1]}
    
    return _node

async def _human_queue_node(state: TeamState) -> dict:
    return {
        "messages": [
            AIMessage(content="[routed to human queue - supervisor confidence too low]")
        ]
    }

def _pick_specialist(state: TeamState) -> str:
    routing = state.get("routing")
    if routing is None or routing.confidence < SUPERVISOR_CONFIDENCE_MIN:
        return "human_queue"
    return routing.specialist

def build_team_graph(checkpointer=None):
    """Compile the multi-agent team graph."""
    graph = StateGraph(TeamState)
    graph.add_node("supervisor", _supervisor_node)
    graph.add_node("billing", _make_specialist_node("billing"))
    graph.add_node("technical", _make_specialist_node("technical"))
    graph.add_node("account", _make_specialist_node("account"))
    graph.add_node("human_queue", _human_queue_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _pick_specialist,
        {
            "billing": "billing",
            "technical": "technical",
            "account": "account",
            "human_queue": "human_queue"
        }
    )
    for node in ("billing", "technical", "account", "human_queue"):
        graph.add_edge(node, END)
    return graph.compile(checkpointer=checkpointer)

async def main() -> None:
    from support_agents.triage import TKT_10001_BODY

    graph = build_team_graph()
    result = await graph.ainvoke(
        {
            "body": TKT_10001_BODY,
            "tenant": "acme-corp",
            "messages": [HumanMessage(content=f"Triage this ticket:\n\n{TKT_10001_BODY}")]
        }
    )
    
    print(f"supervisor -> {result['routing'].specialist} "
          f"(confidence {result['routing'].confidence:.2f})")
    for message in result["messages"]:
        prefix = type(message).__name__
        print(f"    [{prefix}] {message.content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())