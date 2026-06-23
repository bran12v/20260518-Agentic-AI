"""Orchestrator-Worker Graph.

Same three specialists as the supervisor team. Different topology:

    START -> decompose -> workers (parallel) -> synthesize -> END
    
The supervisor ROUTES one ticket to one specialist. The ochestrator
DECOMPOSES one complex request into N subtasks, runs the relavent specialists
as WORKERS in parallel, and synthesizes their findings into one deliverable.
"""

import asyncio
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field

from support_agents.config import langchain_chat_model
from support_agents.LangGraph.specialists import SPECIALIST_BUILDERS
from support_agents.LangGraph.supervisor import SupervisorSpecialist

class Subtask(BaseModel):
    """One slice of the request, assigned to one specialist."""

    # any use of specialist language in this file is referring to WORKERS !!!!!
    specialist: SupervisorSpecialist = Field(
        description="Which specialist handles this slice of the request."
    )
    instruction: str = Field(
        description="What this specialist should produce for the plan."
    )

class DecompositionPlan(BaseModel):
    """The orchestrator's breakdown of a complex request."""

    # a LIST, not a single pick - supervisor vs orchestrator diff
    subtasks: list[Subtask] = Field(
        description="One per domain the request touches. Omit domains it doesn't"
    )
    rationale: str = Field(
        max_length=240, description="One or two sentances on why this breakdown."
    )

class PlanState(TypedDict, total=False):
    """State for the orchestrator-worker graph."""

    request: str
    tenant: str | None
    plan: DecompositionPlan
    findings: list[str] # plain list - one node writes it all at once with no reducer
    final_plan: str

ORCHESTRATOR_SYSTEM = (
    "You are the ORCHESTRATOR for a customer-support platform. You receive ONE "
    "complex request that may span billing, technical, and account domains. "
    "Break it into subtasks — at most one per specialist — assigning each to "
    "the specialist that owns it:\n\n"
    "- billing: invoices, refunds, payment failures, subscription changes.\n"
    "- technical: integration errors, API failures, outages, bug reports.\n"
    "- account: user management, permissions, SSO, provisioning, entitlements.\n\n"
    "Only create subtasks for domains the request actually touches. A request "
    "that's purely billing yields ONE subtask, not three."
)

async def _decompose_node(state: PlanState) -> dict:
    model = langchain_chat_model().with_structured_output(DecompositionPlan)
    request = state["request"]
    if state.get("tenant"):
        request = f"Tenant: {state["tenant"]}\n\n{request}"
    plan = await model.ainvoke(
        [
            SystemMessage(content=ORCHESTRATOR_SYSTEM),
            HumanMessage(content=request)
        ]
    )
    assert isinstance(plan, DecompositionPlan)
    return {"plan": plan}

def _make_workers_node():
    """Build each specialist ONCE; the node reuses them across every request."""
    workers = {name: build() for name, build in SPECIALIST_BUILDERS.items()}

    async def _node(state: PlanState) -> dict:
        plan = state['plan']
        async def run_one(sub: Subtask) -> str:
            # each worker is a full ReAct specialist - the same one the
            # supervisor would have routed to. Here we are running multiple at once.
            agent = workers[sub.specialist]
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=sub.instruction)]}
            )
            return f"## {sub.specialist}\n{result["messages"][-1].content}"
        
        # fan-out: every subtask runs concurrently, not one after the other
        sections = await asyncio.gather(*(run_one(subtask) for subtask in plan.subtasks))
        return {"findings": list(sections)}
    
    return _node

SYNTHESIS_SYSTEM = (
    "You are the orchestrator's SYNTHESIS step. You are given the original "
    "request and the findings each specialist produced for their slice. Merge "
    "them into ONE coherent deliverable with a section per domain, ordered by "
    "the sequence the work should happen in. Do not invent details no "
    "specialist provided."
)

async def _synthesize_node(state: PlanState) -> dict:
    model = langchain_chat_model()
    joined = "\n\n".join(state["findings"])
    result = await model.ainvoke(
        [
            SystemMessage(content=SYNTHESIS_SYSTEM),
            HumanMessage(
                content=f"Original request:\n{state["request"]}\n\n"
                f"Specialist findings:\n\n{joined}"
            )
        ]
    )
    return {"final_plan": result.content} # nodes return dictionaries -> dict's update the state object

def build_orchestrator_graph():
    """Compile the orchestrator-worker graph: decompose -> workers -> synthesize"""
    graph = StateGraph(PlanState)
    graph.add_node("decompose", _decompose_node)
    graph.add_node("specialists", _make_workers_node())
    graph.add_node("synthesize", _synthesize_node)

    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "specialists")
    graph.add_edge("specialists", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()

async def main() -> None:
    graph = build_orchestrator_graph()
    request = (
        "We're migrating Globex from the legacy plan to enterprise. Produce an "
        "onboarding plan: reconcile their two outstanding duplicate invoices, "
        "validate the API integration against the new enterprise rate limits, "
        "and provision SSO for their 200 users."
    )
    result = await graph.ainvoke({"request": request, "tenant": "globex-inc"})

    print(f"decomposed into {len(result["plan"].subtasks)} subtasks:")
    for sub in result["plan"].subtasks:
        print(f"    - {sub.specialist}: {sub.instruction}")
    print("\n=== synthesized plan ===")
    print(result["final_plan"])

if __name__ == "__main__":
    asyncio.run(main())