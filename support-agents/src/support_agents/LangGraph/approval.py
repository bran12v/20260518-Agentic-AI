"""Human-in-the-loop approval gate."""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt # magic item

class ApprovalState(TypedDict, total=False):
    """State for the approval-gate demo graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    draft: str
    approved_draft: str
    was_rejected: bool

async def _draft_node(state: ApprovalState) -> dict:
    """Placeholder."""
    draft = state.get("draft") or "Hello"
    return {"draft": draft}

async def _approval_gate(state: ApprovalState) -> dict:
    """Pause the graph and wait for a human decision on the draft."""
    decision: str = interrupt(f"Approve this draft?\n\n---\n{state["draft"]}\n---")
    decision = (decision or "").strip()
    if decision.lower() == "approved":
        return {"approved_draft": state["draft"]}
    if decision.lower().startswith("edit:"):
        return {"approved_draft": decision[len("edit:") :].strip()}
    return {"was_rejected": True}

async def _send_node(state: ApprovalState) -> dict:
    """Pretend-send the approved draft. A real flow would POST back to support api as new conversation turn."""
    if state.get("was_rejected"):
        return {
            "messages": [AIMessage(content=f"[draft rejected - no reply sent to customer]")]
        }
    approved = state.get("approved_draft", "")
    return {
        "messages": [AIMessage(content=f"[sent to customer:\n{approved}]")]
    }

def build_approval_graph(checkpointer):
    """Build the approval-gate graph. Must receive a checkpointer - interrupt
    only works with one."""
    graph = StateGraph(ApprovalState)
    graph.add_node("draft", _draft_node)
    graph.add_node("approval_gate", _approval_gate)
    graph.add_node("send", _send_node)

    graph.add_edge(START, "draft")
    graph.add_edge("draft", "approval_gate")
    graph.add_edge("approval_gate", "send")
    graph.add_edge("send", END)
    return graph.compile(checkpointer=checkpointer)

async def _run_with_resume(thread_id: str, draft: str, decision: str) -> None:
    """Helper: invoke the approval graph, capture the interrupt, resume with 'decision'."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command

    graph = build_approval_graph(MemorySaver())
    cfg = {"configurable": {"thread_id": thread_id}}

    result = await graph.ainvoke({"draft": draft}, config=cfg)
    print("after first invoke:")
    print(f"    __interrupt__ = {result.get('__interrupt__')}")

    result = await graph.ainvoke(Command(resume=decision), config=cfg)
    print(f"after resume ({decision}):")
    for msg in result["messages"]:
        print(f"    {msg.content}")

async def demo_approve() -> None:
    """Full approve cycle."""
    await _run_with_resume(
        thread_id="TKT-10001-draft",
        draft="Thanks for flagging the duplicate invoice line item. We're investigating.",
        decision="approved"
    )
    
async def demo_edit() -> None:
    """Full approve cycle."""
    await _run_with_resume(
        thread_id="TKT-10002-draft",
        draft="Original text",
        decision="edit: revised text the human-in-the-loop wrote to adjust the original."
    )

def main() -> None:
    """Argv-driven dispatcher for running our approval state graph"""

    import asyncio
    import sys
    flags = {
        "--approve": demo_approve,
        "--edit": demo_edit
    }
    for flag, fn in flags.items():
        if flag in sys.argv:
            asyncio.run(fn())
            return

if __name__ == "__main__":
    main()