"""support-agents' HTTP client for support-api

Set up the support-api HTTP contract (URL paths + JSON shapes) for our agent's tools
to utilize.
"""
import os
from typing import Any

import httpx

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000").rstrip("/")

# Getting individual tickets
async def get_ticket(ticket_id: str) -> dict[str, Any]:
    """GET /tickets/{id}"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}/tickets/{ticket_id}")
        response.raise_for_status()
        return response.json()

# Getting all tickets
async def list_tickets(
    tenant: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """GET /tickets?filters..."""
    params: dict[str, Any] = {"limit": limit}
    if tenant:
        params["tenant"] = tenant
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}/tickets", params=params)
        response.raise_for_status()
        return response.json()["items"]