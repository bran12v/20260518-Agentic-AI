""" Async batch ticket classifier."""

import asyncio
from dataclasses import dataclass
import sys
import time

from langchain_core.rate_limiters import InMemoryRateLimiter
from support_agents.config import langchain_chat_model
from support_agents.schemas import TriageSuggestion
from support_agents.LangChain.triage_chain import _PREP, _CLASSIFY_PROMPT

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential
)

def build_batch_chain():
    """First Version - no rate limiter, just batch processer."""
    model = langchain_chat_model().with_structured_output(TriageSuggestion)
    return _PREP | _CLASSIFY_PROMPT | model

def build_rate_limited_chain(requests_per_second: float = 2.0   ):
    """Same shape as build_classifier_chain() but with a rate limiter
    on the model. Every ainoke/ abatch call takes a token from the limiter
    before sending and the limiter blocks requests until a token is available."""
    limiter = InMemoryRateLimiter(
        requests_per_second=requests_per_second,
        check_every_n_seconds=0.05,
        max_bucket_size=10
    )
    model = langchain_chat_model(rate_limiter=limiter).with_structured_output(TriageSuggestion)
    return _PREP | _CLASSIFY_PROMPT | model

@dataclass
class BatchResult:
    """One classification outcome - either a TriageSuggestion or the error."""
    ticket_id: str
    suggestion: TriageSuggestion | None
    error: str | None

async def classify_batch(
    tickets: list[dict],
    concurrency: int = 20,
    requests_per_second: float = 2.0
) -> list[BatchResult]:
    """Classify every ticket in 'tickets' concurrently.
    
    'concurrency' is a semaphore cap on how many classification can be 'in flight'
    at one time. Caps memory / socket pressure."""
    chain = build_rate_limited_chain(requests_per_second)
    sem = asyncio.Semaphore(concurrency)

    async def _classify_one(ticket_id: str, body: str) -> BatchResult:
        """Classify one ticket, retrying transient failures with exponential back-off.
        
        In production, limit what errors the back-off occurs on. (rate-limits or api connection errors)"""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(4),
            wait=wait_exponential(multiplier=1, min=1, max=30),
            retry=retry_if_exception_type(Exception),
            reraise=True
        ):
            with attempt:
                suggestion = await chain.ainvoke({"body": body})
                return BatchResult(ticket_id=ticket_id, suggestion=suggestion, error=None)
        # Unreachable - 'reraise=True' propagates the final error.
        raise RuntimeError("Retry loop exited without reaching a result.")

    async def _guarded(ticket) -> BatchResult:
        async with sem:
            try:
                return await _classify_one(ticket["id"], ticket["body"])
            except Exception as err:
                return BatchResult(
                    ticket_id=ticket["id"], suggestion=None, error=str(err)
                )
    return await asyncio.gather(*(_guarded(ticket) for ticket in tickets))
    


async def benchmark(sample_size: int = 10) -> None:
    """Compare serial vs concurrent classification on a small sample. Pulls
    real tickets from support-api so timing reflects real network + LLM latency."""
    from support_agents import api_client
    from support_agents.LangChain.triage_chain import build_classifier_chain

    tickets = await api_client.list_tickets(status="open", limit=sample_size)
    chain = build_classifier_chain()
    bodies = [{"body": ticket["body"]} for ticket in tickets]

    timeStart = time.perf_counter()
    for body in bodies:
        await chain.ainvoke(body)
    print(f"serial ({sample_size}x): {time.perf_counter() - timeStart:.2f}s")

    timeStart = time.perf_counter()
    # await asyncio.gather(*(chain.ainvoke(body) for body in bodies))
    await classify_batch(tickets=tickets, concurrency=5)
    print(f"gather ({sample_size}x): {time.perf_counter() - timeStart:.2f}s")


async def main() -> None:
    if "--bench" in sys.argv:
        await benchmark()
        return
    from support_agents import api_client
    tickets = await api_client.list_tickets(status="open", limit=50)
    print(f"Fetched {len(tickets)} tickets. Classifying...")
    time_start = time.perf_counter()
    results = await classify_batch(tickets, requests_per_second=2.0, concurrency=10)
    elasped = time.perf_counter() - time_start

    ok = sum(1 for r in results if r.suggestion is not None)
    failed = len(results) - ok
    print(f"\nClassied {ok}/{len(results)} in {elasped:.1f}s ({failed} failed)")

    for result in results[:5]: 
        if result.suggestion:
            suggestion = result.suggestion
            print(f"    {result.ticket_id}: {suggestion.category}/{suggestion.priority} - {suggestion.summary}")
        else:
            print(f"    {result.ticket_id}: FAILED - {result.error}")

if __name__ == "__main__":
    asyncio.run(main())