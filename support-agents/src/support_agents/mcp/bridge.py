"""MCP client-side bridge to LangChain tools."""

from contextlib import asynccontextmanager
import json
import sys
from typing import Any

from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters, stdio_client


def _make_langchain_tool(session: ClientSession, mcp_tool: Any) -> StructuredTool:
    """Turn one MCP tool descriptors into a LangChain 'StructuredTool'"""

    async def _invoke(**kwargs):
        result = await session.call_tool(mcp_tool.name, arguments=kwargs)
        if result.isError:
            raise RuntimeError(f"MCP tool {mcp_tool.name} errored")
        return "\n".join(
            part.text for part in result.content if hasattr(part, "text")
        )
    
    return StructuredTool.from_function(
        coroutine=_invoke,
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        args_schema=mcp_tool.inputSchema,
    )

@asynccontextmanager
async def mcp_kb_session():
    """Spawn the KB server subprocess and yield a live, initialized 'ClientSession'.
    Both tools and resources will read over this one session - the connection is a 
    shared resource.
    """
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "support_agents.mcp.kb_server"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

@asynccontextmanager
async def mcp_kb_tools():
    """Yield the server's tools wrapped as LangChain `StructuredTools`s.
    Building the 'mcp_kb_session' - tool discovery is just one thing you do
    with an open session."""

    async with mcp_kb_session() as session:
        listed = await session.list_tools()
        yield [_make_langchain_tool(session, tool) for tool in listed.tools]

async def demo_list_tools() -> None:
    """Spawn the KB server, list the discovered tools and their descriptions."""
    async with mcp_kb_tools() as kb_tools:
        for tool in kb_tools:
            print(f"{tool.name}: {tool.description[:60]}")

async def demo_resources() -> None:
    """List the KB server's resources, then read out corpus."""
    async with mcp_kb_session() as session:
        listed = await session.list_resources()
        for res in listed.resources:
            print(f"resource: {res.uri}     ({res.description})")

        templates = await session.list_resource_templates()
        for res in templates.resourceTemplates:
            print(f"template: {res.uriTemplate}")

        # Read ONE article by its tempalted URI - deterministic, no model turn.
        raw = await session.read_resource("kb://articles/KB-0002")
        article = json.loads(raw.contents[0].text)
        print(f"read kb://articles/KB-0002 -> {article["id"]}: {article["title"]}")

async def demo_with_specialist() -> None:
    """Wire in the MCP 'search_kb' tool into the tech speicalists tool set."""

    from langchain_core.messages import HumanMessage
    from langgraph.prebuilt import create_react_agent

    from support_agents.config import langchain_chat_model
    from support_agents.LangGraph.specialists import TECHNICAL_SYSTEM
    from support_agents.triage_tools import (
        get_ticket_detail,
        list_tenant_open_tickets,
        search_tenant_recent_tickets
    )

    ticket = (
        "Acme-corp (TKT-10002): Integration broken since this morning. We are seeing a lot of 429 errors."
        "Not sure if it is our retry policy or your rate limit."
    )

    async with mcp_kb_tools() as kb_tools:
        all_tools = [
            get_ticket_detail,
            search_tenant_recent_tickets,
            list_tenant_open_tickets
        ] + kb_tools
        agent = create_react_agent(
            langchain_chat_model(), all_tools, prompt=TECHNICAL_SYSTEM
        )
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=f"Triage this ticket:\n\n{ticket}")]}
        )
        print(result["messages"][-1].content)

def main() -> None:
    import asyncio

    flags = {
        "--list-tools": demo_list_tools,
        "--resources": demo_resources,
        "--with-specialist": demo_with_specialist
    }
    for flag, fn in flags.items():
        if flag in sys.argv:
            asyncio.run(fn())
            return
        
if __name__ == "__main__":
    main()