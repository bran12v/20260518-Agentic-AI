import json
import sqlite3
from typing import Any


# go from sqlite3 row -> dict (ticket)
def _row_to_ticket(row: sqlite3.Row) -> dict[str, Any]:
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
    where, params = [], []
    if priority:
        where.append("priority = ?")
        params.append(priority)
    if tenant:
        where.append("tenant = ?")
        params.append(tenant)
    if status:
        where.append("status = ?")
        params.append(status)

    sql = "SELECT * FROM tickets"
    if where:
        sql += " WHERE " + " AND ".join(where) # WHERE priority = ? AND tenant = ? AND status = ?
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    # sql = SELECT * FROM tickets WHERE priority = ? AND tenant = ? AND status = ? ORDER BY created_at DESC LIMIT ?
    # params = [normal, acme-corp, open, 100]
    
    return [_row_to_ticket(row) for row in conn.execute(sql, params).fetchall()] # list of ticket dicts


def get_ticket(conn, ticket_id):
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    return _row_to_ticket(row) if row else None

def insert_ticket(conn, ticket): 
    # execute(SQLString, Parameters)
    conn.execute(
        """INSERT INTO tickets
        (id, title, body, priority, status, category, tenant,
        customer_id, assignee, channel, tags, created_at, updated_at)
        VALUES (:id, :title, :body, :priority, :status, :category, :tenant, 
        :customer_id, :assignee, :channel, :tags, :created_at, :updated_at)""",
        {**ticket, "tags": json.dumps(ticket.get("tags", []))}
    )