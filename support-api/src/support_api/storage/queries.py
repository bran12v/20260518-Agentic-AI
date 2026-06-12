import json
from typing import Any

import psycopg

# go from sqlite3 row -> dict (ticket)
def _row_to_ticket(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "priority": row["priority"],
        "status": row["status"],
        "category": row["category"],
        "tenant": row["tenant"],
        "customer_id": row["customer_id"],
        "assignee": row["assignee"],
        "channel": row["channel"],
        "tags": json.loads(row["tags"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

# list our tickets
def list_tickets(conn, priority=None, tenant=None, status=None, limit=100):
    """Returns tickets matching optional filters, newest first"""
    where: list[str] = []
    params: list[Any] = []

    if priority:
        where.append("priority = %s")
        params.append(priority)
    if tenant:
        where.append("tenant = %s")
        params.append(tenant)
    if status:
        where.append("status = %s")
        params.append(status)

    sql = "SELECT * FROM tickets"
    if where:
        sql += " WHERE " + " AND ".join(where) # WHERE priority = %s AND tenant = %s AND status = %s
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    # sql = SELECT * FROM tickets WHERE priority = %s AND tenant = %s AND status = %s ORDER BY created_at DESC LIMIT %s
    # params = [normal, acme-corp, open, 100]
    
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return [_row_to_ticket(row) for row in cur.fetchall()] # list of ticket dicts


def get_ticket(conn, ticket_id):
    with conn.cursor() as cur:
        conn.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        row = cur.fetchone()
    return _row_to_ticket(row) if row else None

def insert_ticket(conn, ticket): 
    # execute(SQLString, Parameters)
    conn.execute(
        """
        INSERT INTO tickets
            (id, title, body, priority, status, category, tenant,
            customer_id, assignee, channel, tags, created_at, updated_at)
        VALUES (%(id)s, %(title)s, %(body)s, %(priority)s, %(status)s, %(category)s, %(tenant)s, 
            %(customer_id)s, %(assignee)s, %(channel)s, %(tags)s, %(created_at)s, %(updated_at)s)
        """,
        {**ticket, "tags": json.dumps(ticket.get("tags", []))}
    )