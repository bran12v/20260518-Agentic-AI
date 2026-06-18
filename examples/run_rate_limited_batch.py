import asyncio
import time
from support_agents import api_client
from support_agents.batch import classify_batch

SAMPLE_SIZE = 20
REQUESTS_PER_SECOND = 2.0
CONCURRENCY = 10

async def main() -> None:
    tickets = await api_client.list_tickets(status="open", limit=SAMPLE_SIZE)
    time_start = time.perf_counter()
    results = await classify_batch(
        tickets=tickets,
        requests_per_second=REQUESTS_PER_SECOND,
        concurrency=CONCURRENCY
    )
    elapsed = time.perf_counter() - time_start
    number_of_successful_suggestions = sum(1 for r in results if r.suggestion is not None)
    print(f"{number_of_successful_suggestions}/{len(results)} in {elapsed:.1f}s @ {REQUESTS_PER_SECOND} req/s")

if __name__ == "__main__":
    asyncio.run(main())
