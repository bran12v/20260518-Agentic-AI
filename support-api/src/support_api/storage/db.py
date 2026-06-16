"""PosgreSQL DB file"""

import json
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


#schema path
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
#json files path
_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
#db path
DEFAULT_DATABASE_URL = "postgresql://support:support_dev@db:5432/support"

def _connection_string(database_url: Path | str | None) -> Path | str:
    """Priority: explicit db_url arg > db_url env var > Module default"""
    return database_url or os.environ.get("DATABASE_URL") or DEFAULT_DATABASE_URL

# connect to the db
def connect(database_url: Path | str | None = None) -> psycopg.Connection:
    """Open a psycopg connection with rows as dicts, postgres equivalent of what we had for sqlite"""
    return psycopg.connect(_connection_string(database_url), row_factory=dict_row)

# init of the db - create all our tables
def init_db(database_url: Path | str | None = None) -> None:
    conn = connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8")) # This will read our schema file and execute the DDL.
        conn.commit()
    finally:
        conn.close()

# seeding of the db
def seed_from_json(
        database_url: str | None = None,
        customers_json: Path | None = None,
        tickets_json: Path | None = None,
    ) -> tuple[int, int]:
    """Load in the JSON seed files into the DB."""
    customers_json = customers_json or (_DATA_DIR / "customers.json")
    tickets_json = tickets_json or (_DATA_DIR / "tickets.json")

    customers = json.loads(Path(customers_json).read_text(encoding="utf-8"))
    tickets = json.loads(Path(tickets_json).read_text(encoding="utf-8"))


    conn = connect(database_url)
    try:
        with conn.cursor() as cur:
        # Insert statement for all the data in customers.json, make a row - many times
            cur.executemany( 
                """
                INSERT INTO customers
                    (id, name, tenant, plan, primary_contact_email, created_at)
                VALUES (%(id)s, %(name)s, %(tenant)s, %(plan)s, %(primary_contact_email)s, %(created_at)s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    tenant = EXCLUDED.tenant,
                    plan = EXCLUDED.plan,
                    primary_contact_email = EXCLUDED.primary_contact_email,
                    created_at = EXCLUDED.created_at
                """,
                customers
            )
            # Insert statement for all the data in tickets.json
            cur.executemany( # not going to duplicate seed, its going to upsert (insert/update)
                """
                INSERT INTO tickets
                    (id, title, body, priority, status, category, tenant,
                    customer_id, assignee, channel, tags, created_at, updated_at)
                VALUES (%(id)s, %(title)s, %(body)s, %(priority)s, %(status)s, %(category)s, %(tenant)s,
                    %(customer_id)s, %(assignee)s, %(channel)s, %(tags)s, %(created_at)s, %(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    body = EXCLUDED.body,
                    priority = EXCLUDED.priority,
                    status = EXCLUDED.status,
                    category = EXCLUDED.category,
                    tenant = EXCLUDED.tenant,
                    customer_id = EXCLUDED.customer_id,
                    assignee = EXCLUDED.assignee,
                    channel = EXCLUDED.channel,
                    tags = EXCLUDED.tags,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
                """,
                [ 
                    {
                        **t, 
                        "tags": json.dumps(t.get("tags", []))
                    } 
                    for t in tickets
                ]
            )
        conn.commit()
    finally:
        conn.close()
    return len(customers), len(tickets)