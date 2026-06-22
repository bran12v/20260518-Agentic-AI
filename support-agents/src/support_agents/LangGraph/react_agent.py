
from typing import Annotated, TypedDict
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, create_react_agent
from support_agents.config import langchain_chat_model
from support_agents.graph_viz import draw_graphs
from support_agents.triage_tools import TRIAGE_TOOLS

class ReActState(TypedDict):
    """State for the manual ReAct graph.
    
    - 'messages' - uses the standard add_messages reducer (append on return).
    - 'reasoning_trace' - uses plain list concatenation via 'operator.add' - returning
    '{"reasoning_trace": ["new thought"]}' appends to the list"""

    messages: Annotated[list[BaseMessage], add_messages]
    reasoning_trace: Annotated[list[str], operator.add]

REACT_SYSTEM = (
    "You triage customer-support tickets. Before EACH tool call or final "
    "answer, write a brief THOUGHT explaining your reasoning. Format each "
    "turn as:\n\n"
    "Thought: <1-2 sentence reasoning — what do I know, what am I checking, why>\n"
    "Action: <call a tool OR give the final classification>\n\n"
    "The Thought line is stored for audit. Be specific about which facts you "
    "are checking and why — not 'I will gather information', but 'the body "
    "mentions TKT-11042 so I will look it up to check the tenant's pattern'.\n\n"
    "Tool discipline: only call `get_ticket` when the body contains a literal "
    "`TKT-NNNNN` identifier. Invoice numbers (`INV-...`), dates, and other "
    "digit-containing codes are NOT ticket IDs. If no ticket ID appears in the "
    "body, classify from the body text alone — do not invent IDs to look up."
)

def _extract_thought(content: str) -> str | None:
    """Pull the 'Thought:' out of the model's context. Return None if the model
    did not produce a single thought."""
    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("thought:"):
            return line[len("thought:") :].strip()
    return content.strip() if content.strip() else None

# Node Factory
def _react_node_factory():
    """Bind tools at build time; return a node that captures a thought."""
    model_with_tools = langchain_chat_model().bind_tools(TRIAGE_TOOLS)

    async def _react(state: ReActState) -> dict:
        response = await model_with_tools.ainvoke(state["messages"])
        thought = _extract_thought(response.content or "")
        updates: dict = {"messages": [response]}
        if thought: 
            updates["reasoning_trace"] = [thought]
        return updates
    
    return _react

# Conditional call
def _should_continue(state: ReActState) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END

# Build function
def build_manual_react_graph():
    """Handcrafted ReAct graph agent: reason -> (tools -> reason)* -> END"""
    graph = StateGraph(ReActState)
    graph.add_node("reason", _react_node_factory())
    graph.add_node("tools", ToolNode(TRIAGE_TOOLS, handle_tool_errors=True))

    graph.add_edge(START, "reason")
    graph.add_conditional_edges("reason", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "reason")
    return graph.compile()

# Prebuilt agent
def build_prebuilt_react_agent(checkpointer=None):
    """This is the prebuilt react agent -> same pattern, less code."""
    model = langchain_chat_model()
    return create_react_agent(
        model,
        TRIAGE_TOOLS,
        prompt=REACT_SYSTEM,
        checkpointer=checkpointer
    )

def print_graphs() -> None:
    draw_graphs([
        ("Manual ReAct graph", build_manual_react_graph),
        ("Prebuilt creat_react_agent", build_prebuilt_react_agent)
    ])

async def stream_demo() -> None:
    """Stream the manual ReAct graph node-by-node, printing each thought as
    it's produced. Used in W6 D1 Part 4 to show reasoning unfold live."""
    from support_agents.triage import TKT_10001_BODY

    graph = build_manual_react_graph()
    async for event in graph.astream(
        {
            "messages": [
                SystemMessage(content=REACT_SYSTEM),
                HumanMessage(content=f"Triage:\n\n{TKT_10001_BODY}"),
            ],
            "reasoning_trace": [],
        },
    ):
        for node, update in event.items():
            for thought in update.get("reasoning_trace", []):
                print(f"  [{node}] THOUGHT: {thought}")
            if update.get("messages") and node == "tools":
                print(f"  [{node}] tool ran")

async def main() -> None:
    from support_agents.triage import TKT_10001_BODY
    import sys

    if "--stream" in sys.argv:
        await stream_demo()
        return


    print("--- Manual ReAct ---")
    manual = build_manual_react_graph()
    result = await manual.ainvoke(
        {
            "messages": [
                SystemMessage(content=REACT_SYSTEM),
                HumanMessage(content=f"Triage this ticket:\n\n{TKT_10001_BODY}")
            ],
            "reasoning_trace": [],
        }
    )
    print("Reasoning trace:")
    for i, thought in enumerate(result["reasoning_trace"], 1):
        print(f"    {i}. {thought}")
    print(f"\nFinal reply: {result["messages"][-1].content}")

    print("\n--- Prebuilt create_react_agent ---")
    prebuilt = build_prebuilt_react_agent()
    prebuilt_result = await prebuilt.ainvoke(
        {"messages": [HumanMessage(content=f"Triage this ticket:\n\n{TKT_10001_BODY}")]}
    )
    print(f"Final reply: {prebuilt_result["messages"][-1].content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())