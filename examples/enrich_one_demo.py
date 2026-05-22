import asyncio

import httpx
import structlog

from support_api.enrich import enrich_ticket
from support_api.filters import load_tickets

structlog.configure()

async def main() -> None:
    ticket = load_tickets()[0]
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            enriched = await enrich_ticket(ticket, client)
        except httpx.RequestError as err:
            print(f"Network unreachable ({type(err).__name__}); skip or retry later")
            return
        print(f"{enriched['id']} -> {enriched['enrichment']}")

if __name__ == "__main__":
    asyncio.run(main())