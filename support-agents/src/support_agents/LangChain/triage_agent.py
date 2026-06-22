"""Tool calling triage AI agent."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage, ToolMessage

from support_agents.config import langchain_chat_model
from support_agents.triage_tools import TRIAGE_TOOLS
from support_agents.triage import TriageSuggestion, TKT_10001_BODY

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.main")

MAX_TOOL_CALLS = 6 # safety cap, so the agent doesnt think forever 

AGENT_SYSTEM = (
    "You triage inbound customer-support tickets. You can call tools to gather "
    "context before classifying — check the tenant's recent and open tickets if "
    "the body mentions repeat issues or references another case. Prefer fewer "
    "tool calls when the body alone is enough to classify."
)

FINAL_INSTRUCTION = (
    "You have gathered enough context. Produce a final TriageSuggestion for the " \
    "original ticket. Use the tool results above as context for your object."
)

async def run_triage_agent(body: str, tenant: str | None = None) -> TriageSuggestion:
    """Run the tool loop over the 'body', then coerce the final answer into a 
    'TriageSuggestion' object. Returns when the model stops calling tools (or hits the cap)"""
    model_with_tools = langchain_chat_model().bind_tools(TRIAGE_TOOLS)
    tool_registry = {tool.name: tool for tool in TRIAGE_TOOLS}

    user_prompt = f"Triage this inbound ticket. Use tools if helpful. \n\n{body}"
    if tenant:
        user_prompt = f"Tenant: {tenant}\n\n{user_prompt}"

    messages: list[BaseMessage] = [
        SystemMessage(content=AGENT_SYSTEM),
        HumanMessage(content=user_prompt),
    ]

    for _ in range(MAX_TOOL_CALLS):
        response = await model_with_tools.ainvoke(messages)
        assert isinstance(response, AIMessage)
        messages.append(response)
        if not response.tool_calls:
            break
        # Execute every tool call the ai requested
        for tool_call in response.tool_calls:
            tool = tool_registry[tool_call["name"]]
            result = await tool.ainvoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    classifier = langchain_chat_model().with_structured_output(TriageSuggestion)
    final_messages = messages + [HumanMessage(content=FINAL_INSTRUCTION)]
    result = await classifier.ainvoke(final_messages)
    assert isinstance(result, TriageSuggestion)
    return result

async def inspect_tool_calls(prompt: str) -> AIMessage:
    """Run the model with the tools bound but we aren't going to execute any tool calls just yet -
    just return the AIMessage so we can see what 'bind_tools()' produces."""
    model_with_tools = langchain_chat_model().bind_tools(TRIAGE_TOOLS)
    response = await model_with_tools.ainvoke(
        [
            SystemMessage(content="You triage tickets. Use tools to gather context."),
            HumanMessage(content=prompt),
        ]
    )
    assert isinstance(response, AIMessage)
    print("content:", repr(response.content))
    print("tool_calls:", response.tool_calls)
    return response

async def main() -> None:
    import sys

    if "--inspect" in sys.argv:
        await inspect_tool_calls("What recent tickets does acme-corp have?")
        return
    
    result = await run_triage_agent(TKT_10001_BODY, tenant="acme-corp")
    print(f"category:           {result.category}")
    print(f"priority:           {result.priority}")
    print(f"summary:            {result.summary}")
    print(f"suggest_team:       {result.suggest_team}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())