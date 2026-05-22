import asyncio
from typing import Any

import httpx
import structlog

_log = structlog.get_logger(__name__)

_DEFAULT_CONCURRENCY = 10

# asnyc - on function definitions
# await - on fucntion calls
async def enrich_ticket(
    ticket: dict[str, Any],
    client: httpx.AsyncClient,
    base_url: str = "https://httpbin.org"
) -> dict[str, Any]:
    """Fetch 'enrichment data' for a single ticket.
    
    Return a new dict - never mutates the input. The enrichment
    payload is whatever the mock endpoint echoes back under
    the 'args' param"""
    _log.info("enrich_started", ticket_id=ticket["id"])

    # python does lazy evaluation, other lang's do eager evaluation
    response = await client.get(f"{base_url}/get", params={"customer_id": ticket["customer_id"]})# res, req

    response.raise_for_status() # prevents silent success of errors

    echoed = response.json().get("args", {})

    _log.info("enrich_completed", ticket_id=ticket["id"], status=response.status_code)

    return { **ticket, "enrichment": echoed }

# multiple requests going out at the same time
async def enrich_batch(
    tickets: list[dict[str, Any]],
    client: httpx.AsyncClient,
    concurrency: int = _DEFAULT_CONCURRENCY,
    base_url: str = "https://httpbin.org"
) -> list[dict[str, Any]]:
    """Enrich many tickets concurrently (at the same time), capped by a semaphore"""
    semaphore = asyncio.Semaphore(concurrency)

    async def _one(ticket: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await enrich_ticket(ticket, client, base_url=base_url)
        
    return await asyncio.gather(*(_one(ticket) for ticket in tickets))