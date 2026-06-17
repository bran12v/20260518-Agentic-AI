"""
The triage chain that we have so far is BLIND - it only sees the ticket body.
A real triage agent should be able to explore and look around before commiting to 
a classification. Tools will give the LLM this capability.

Each tool is a one-liner wrapper around a function from our api_client.
The doc-string is the model's ONLY DESCRIPTION of the tool and how to use it.
"""

from langchain_core.tools import tool

from support_agents import api_client

# getting individual ticket details
@tool
async def get_ticket_detail(ticket_id: str) -> dict:
    """Return the full record for one ticket by ID.
    ticket ID is structured as TKT-##### where each # symbol represents
    a number from 0-9.
    
    Use this when you already know the ticket ID and need fields like 
    customer_id, created_at, current category/priority, or the tenant.
    """
    return await api_client.get_ticket(ticket_id)


# searching tenants recent tickets
@tool
async def search_tenant_recent_tickets(tenant: str, limit: int = 20) -> list[dict]:
    """List the most recent tickets for a tenant (any status).

    Use to check whether the current issue is a reoccurring pattern for this customer -
    e.g., the tenant opened 3 billing ticekts this month. Pass a tenant name (string), 
    and a limit (number of results to return); default 20, a lower number is fine if 
    you need a small sample.
    """
    return await api_client.list_tickets(tenant=tenant, limit=limit)

# listing tenants open tickets