"""Minimal MCP server exposing a single KB tool.

Runs as a standalone subprocess."""

import json

from mcp.server.fastmcp import FastMCP

# stub corpus: we are going to replace this with RAG/pgvector-backed search next week.
_ARTICLES: list[dict] = [
    {
        "id": "KB-0001",
        "title": "How to reconcile a duplicate invoice line item",
        "category": "billing",
        "snippet": (
            "When an invoice shows two identical line items, check the seat-count "
            "history first. Duplicates typically result from a provisioning "
            "replay — the system bills once per provisioning event, and replays "
            "produce a second charge."
        ),
    },
    {
        "id": "KB-0002",
        "title": "Integration retry storms and the 429 loop",
        "category": "technical",
        "snippet": (
            "If a customer integration is producing 429 errors, check whether "
            "their retry policy has jitter. Integrations without jitter create "
            "correlated retry waves that make rate-limit recovery slow."
        ),
    },
    {
        "id": "KB-0003",
        "title": "SSO provisioning for a new admin user",
        "category": "account",
        "snippet": (
            "To add an admin via SSO, the tenant's IdP admin must update the "
            "group mapping in the SAML assertion. Self-service admin creation "
            "is disabled for tenants on the Enterprise plan."
        ),
    },
    {
        "id": "KB-0004",
        "title": "Credit card decline during subscription renewal",
        "category": "billing",
        "snippet": (
            "Auto-renewals retry three times over seven days. If all three fail, "
            "the account enters a seven-day grace period before downgrade."
        ),
    },
    {
        "id": "KB-0005",
        "title": "Data pipeline latency during regional failover",
        "category": "technical",
        "snippet": (
            "Regional failover produces up to 15-minute data pipeline latency "
            "while the warm-standby catches up. Direct customers to the status page."
        ),
    },
]

mcp = FastMCP("support-agents-kb")

@mcp.tool()
def search_kb(query: str, category: str | None = None, top_k: int = 3) -> list[dict]:
    """Search the support KB for articles relavent to a query.
    
    Args:
        query: Free-text search terms (typically a phrase from the ticket body)
        category: Optional category filter - one of 'billing', 'technical',
            'account'. Omit to search all categories.
        top_k: Max number of articles to return. Default 3.
        
    Return a list of '{id, title, category, snippet}' dicts."""

    query_terms = [term.lower() for term in query.split() if len(term) > 2]

    def score(article: dict) -> int:
        if category and article["category"] != category:
            return -1
        kb_article = f"{article["title"]} {article["snippet"]}".lower()
        return sum(1 for term in query_terms if term in kb_article)
    
    scored = [(score(article), article) for article in _ARTICLES] # tuple (#, article)
    scored = [(article_score, article) for article_score, article in scored if article_score > 0] # remove any articles of mismatched categories
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [article for _, article in scored[:top_k]]


@mcp.resource("kb://articles", description="The full KB article corpus as a JSON list.")
def all_articles() -> str:
    """Expose every KB article as one JSON document.
    
    A resource is READ by URI, not called with arguments. A client lists
    resources, picks one by its URI, and reads it - the same shape as
    fetching a file. No tool-calls, no model decisions involved."""
    return json.dumps(_ARTICLES, indent=2)

@mcp.resource("kb://articles/{article_id}", description="A single KB article by id.")
def article_by_id(article_id: str) -> str:
    """Resource TEMPLATE - the 'article_id' placeholder turns one declaration
    into a family of addressable resources - kb://articles/KB-0001, kb://articles/KB-0002 and so on
    The client fills in the id at read time."""

    for article in _ARTICLES:
        if article["id"] == article_id:
            return json.dumps(article, indent=2)
    raise ValueError(f"No KB article {article_id!r}")

def _check() -> None:
    """Print the server's registered surface - tools, resources, and templates."""
    import asyncio

    print("tools:       ", [tool.name for tool in asyncio.run(mcp.list_tools())])
    print("resources:   ", [str(resource.uri) for resource in asyncio.run(mcp.list_resources())])
    print("tempaltes:   ", [template.uriTemplate for template in asyncio.run(mcp.list_resource_templates())])


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        _check()
    else: 
        mcp.run()
