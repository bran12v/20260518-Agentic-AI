"""
Creating a pipeline of generator functions - 
"""
import json
from pathlib import Path
from typing import Any, Iterable, Callable, Iterator

# _ before variable name indicates protected
# __ indicates private
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def stream_tickets(path: Path | None = None) -> Iterator[dict[str, Any]]:
    """ Yield one ticket at time from the JSON file
    
    Before, we loaded all the tickets into memory at once, now:

    We are going to load them in as needed (requested).
    """
    target = path or (_DATA_DIR / "tickets.json")
    with target.open(encoding="utf-8") as fn:
        # yield keyword, turns functions into generators
        for ticket in json.load(fn):
            yield ticket

def where(
        tickets: Iterable[dict[str, Any]], 
        predicate: Callable[[dict[str, Any]], bool] # closure - python will remember values in its scope, even if they arent in memory anymore
) -> Iterator[dict[str, Any]]:
    """Where - Filter a ticket stream by an arbitrary function (predicate)"""
    for ticket in tickets:
        if predicate(ticket):
            yield ticket


def tag(
        tickets: Iterable[dict[str, Any]],
        field: str,
        compute: Callable[[dict[str, Any]], Any]
) -> Iterator[dict[str, Any]]:
    """Tag - Add a 'computed' field to each ticket without mutating the input"""
    for ticket in tickets:
        # ** -> dict unpacking -> as if you gave every key value pair as an input
        yield { **ticket, field: compute(ticket) }


def take(
        tickets: Iterable[dict[str, Any]],
        n: int
) -> list[dict[str, Any]]:
    """Take - Materialize the first n tickets from a stream"""
    results: list[dict[str, Any]] = []
    for ticket in tickets:
        if len(results) >= n:
            break
        results.append(ticket)
    return results # this is where the pipeline "ends"


if __name__ == "__main__":
    # generator
    stream = stream_tickets()

    # generator
    high_billing = where(
        stream,
        lambda t: t["priority"] == "high" and t["category"] == "billing"
    )

    # generator
    flagged = tag(
        high_billing,
        "needs_review",
        lambda t: t["status"] in {"open", "in_progress"}
    )

    # list[dict]
    top5 = take(flagged, 5)


    # This pipeline gives the top 5 tickets that are high priority billing in the open/in progress status
    for ticket in top5:
        print(f"{ticket['id']}  [{ticket['status']:<20}]    "
              f"review={ticket['needs_review']} {ticket['title'][:60]}")





    # print(type(stream))
    # first = next(stream)
    # print(f"First ticket: {first['id']}")
    # second = next(stream)
    # print(f"Second ticket: {second['id']}")
    # remaining = sum(1 for _ in stream)
    # print(f"Remaining: {remaining}")

