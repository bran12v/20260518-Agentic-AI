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
        cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
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

def insert_kb_article(conn: psycopg.Connection, article: dict[str, Any]) -> None:
    """Upsert a KB article row."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO kb_articles
                (id, title, category, source_path, body, tags, created_at)
            VALUES (%(id)s, %(title)s, %(category)s, %(source_path)s, %(body)s, %(tags)s, %(created_at)s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                category = EXCLUDED.category,
                source_path = EXCLUDED.source_path,
                body = EXCLUDED.body,
                tags = EXCLUDED.tags
            """,
            {**article, "tags": json.dumps(article.get("tags", []))}, # Values
        )

def insert_kb_chunk(conn: psycopg.Connection, article_id, chunk_index: int, chunk_text: str) -> None:
    """Upsert a chunk with a NULL embedding. embed_kb.py backfill
    If the chunk_text changes, the embedding column is reset to NULL so
    embed_kb.py picks it up on the next run."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO kb_chunks (article_id, chunk_index, chunk_text)
            VALUES (%s, %s, %s)
            ON CONFLICT (article_id, chunk_index) DO UPDATE SET
                chunk_text = EXCLUDED.chunk_text,
                embedding = CASE
                    WHEN kb_chunks.chunk_text IS DISTINCT FROM EXCLUDED.chunk_text
                    THEN NULL
                    ELSE kb_chunks.embedding
                END
            """,
            (article_id, chunk_index, chunk_text),
        )

def update_kb_chunk_embedding(
    conn: psycopg.Connection,
    article_id: str,
    chunk_index: int,
    embedding: list[float]
) -> None:
    """Set the embedding on a existing chunk row. Used by embed_kb.py"""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE kb_chunks
                SET embedding = %s::vector
            WHERE article_id = %s AND chunk_index = %s
            """,
            (_vector_literal(embedding), article_id, chunk_index)
        )

def _vector_literal(embedding: list[float]) -> str:
    """::vector is only going to accept the textual form when it casts to a vector.
    We are doing this to avoid having to write the code to implement this cast ourselves.
    """
    return "[" + ",".join(f"{num:.8f}" for num in embedding) + "]" # [1.00000000,2.00000000,3.00000000] <- string