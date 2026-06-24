"""Checkpointers, thread_id, and resume-after-crash."""

from contextlib import asynccontextmanager

from langgraph.checkpoint.memory import MemorySaver

from support_agents.LangGraph.team_graph import build_team_graph

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

def build_memory_checkpointed_team():
    """In-memory checkpointer - fastest, easiest implementation -> lost on restart."""
    return build_team_graph(checkpointer=MemorySaver())

def thread_config(ticket_id: str, tenant: str | None = None) -> dict:
    """Build the LangGraph `config` dict for a ticket-scoped thread."""
    thread_id = f"{tenant}:{ticket_id}" if tenant else ticket_id
    return {"configurable": {"thread_id": thread_id}}

DEMO_TICKET_ID = "TKT-10042"
DEMO_TENANT = "acme-corp"
DEMO_DB_PATH = "support_agents_LangGraph_threads.sqlite"

async def demo_memory_carryover() -> None:
    """Two ainvoke calls on the same thread_id; shows that state carries across."""

    from langchain_core.messages import HumanMessage

    team = build_memory_checkpointed_team()
    cfg = thread_config(DEMO_TICKET_ID, tenant=DEMO_TENANT)

    await team.ainvoke(
        {
            "body": "Our invoice is wrong.",
            "tenant": DEMO_TENANT,
            "messages": [HumanMessage(content="Triage this ticket.")]
        },
        config=cfg,
    )
    state = await team.aget_state(cfg)
    print(
        f"After first call: {len(state.values['messages'])} messages,"
        f"routing={state.values['routing'].specialist}"
    )

    await team.ainvoke(
        {"messages": [HumanMessage(content="Update: still broken.")]},
        config=cfg
    )
    state = await team.aget_state(cfg)
    print(f"After second call: {len(state.values["messages"])} messages") 

@asynccontextmanager
async def sqlite_checkpointed_team(db_path: str = "support_agents_LangGraph_threads.sqlite"):
    """File-backed async SQLite checkpointer."""
    async with AsyncSqliteSaver.from_conn_string(db_path) as saver:
        yield build_team_graph(checkpointer=saver)

async def demo_sqlite_session_one() -> None:
    """Open a sqlite-backed thread, run one classification, exit. Shows the
    .sqlite file is created on disk."""
    from langchain_core.messages import HumanMessage

    async with sqlite_checkpointed_team(DEMO_DB_PATH) as team:
        cfg = thread_config(DEMO_TICKET_ID, tenant=DEMO_TENANT)
        await team.ainvoke(
            {
                "body": "Invoice is wrong.",
                "tenant": DEMO_TENANT,
                "messages": [HumanMessage(content="Triage.")]
            },
            config=cfg,
        )
        state = await team.aget_state(cfg)
        print(f"Session 1 ended - {len(state.values['messages'])} messages saved")

async def demo_sqlite_session_two() -> None:
    """Re-open the SAME sqlite file from a fresh process. Read the persisted 
    state and print what survived."""
    async with sqlite_checkpointed_team(DEMO_DB_PATH) as team:
        cfg = thread_config(DEMO_TICKET_ID, tenant=DEMO_TENANT)
        state = await team.aget_state(cfg)
        if state.values:
            print(f"Session 2 started - {len(state.values['messages'])} messages loaded")
        else:
            print("Session 2 started - no thread found (run --session1 first)")
    
async def get_state_snapshot(team, ticket_id: str, tenant: str | None = None):
    """Return the latest checkpoint for the ticket's thread. Returns 'None'
    if no threads exist yet."""
    config = thread_config(ticket_id, tenant)
    state = await team.aget_state(config)
    return state if state.values else None

async def demo_history() -> None:
    """Walk the full checkpoint history of the demo thread. Shows step / next /
    message-count for each saved checkpoint."""
    async with sqlite_checkpointed_team(DEMO_DB_PATH) as team:
        cfg = thread_config(DEMO_TICKET_ID, tenant=DEMO_TENANT)
        print("Full history:")
        async for checkpoint in team.aget_state_history(cfg):
            print(
                f"  - step={checkpoint.metadata.get('step')}, "
                f"next={checkpoint.next}, "
                f"messages={len(checkpoint.values.get('messages', []))}"
            )

CRASH_DEMO_DB_PATH = "demo_crash.sqlite"

async def demo_crash_then_resume() -> None:
    """Pause the team graph BEFORE a specialist runs (simulating a crash), 
    then resume from the checkpoint in a fresh saver session."""
    from langchain_core.messages import HumanMessage
    # from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    cfg = thread_config("TKT-10099", tenant=DEMO_TENANT)

    async with AsyncSqliteSaver.from_conn_string(CRASH_DEMO_DB_PATH) as saver:
        team = build_team_graph(checkpointer=saver)
        async for step in team.astream(
            {
                "body": "Invoice wrong.",
                "tenant": DEMO_TENANT,
                "messages": [HumanMessage(content="Triage")],
            },
            config=cfg,
            interrupt_before=["billing"],
        ):
            print(f"step: {list(step.keys())}")
        print("(simulated crash — process exits here)")

    # New connection, same file.
    async with AsyncSqliteSaver.from_conn_string(CRASH_DEMO_DB_PATH) as saver:
        team = build_team_graph(checkpointer=saver)
        state = await team.aget_state(cfg)
        print(f"Resume point: next={state.next}")
        async for step in team.astream(None, config=cfg):
            print(f"step: {list(step.keys())}")

def main() -> None:
    """Argv-driven dispatcher for demos."""
    import asyncio
    import sys

    flags = {
        "--memory": demo_memory_carryover,
        "--session1": demo_sqlite_session_one,
        "--session2": demo_sqlite_session_two,
        "--history": demo_history,
        "--crash-resume": demo_crash_then_resume,
    }
    for flag, fn in flags.items():
        if flag in sys.argv:
            asyncio.run(fn())
            return
    print("usage: python -m support_agents.persistence <flag>")


if __name__ == "__main__":
    main()