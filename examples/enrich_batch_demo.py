import asyncio
import time

import httpx
import structlog

from support_api.enrich import enrich_batch
from support_api.filters import load_tickets

structlog.configure()

async def main() -> None:
    tickets = load_tickets()[:4]
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            results = await enrich_batch(tickets, client, concurrency=2)
        except httpx.RequestError as err:
            print(f"Network unreachable ({type(err).__name__}); skip or retry later")
            return
        elapsed = time.perf_counter() - started
    print(f"\nEnriched {len(results)} tickets in {elapsed}s (concurrency=5)")

if __name__ == "__main__":
    asyncio.run(main())
    