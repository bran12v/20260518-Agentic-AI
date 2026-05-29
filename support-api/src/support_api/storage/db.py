#sqlite3 - stdlib, dont need to install it. It's ready from day one.

import json
import os
from pathlib import Path
import sqlite3

#schema path
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
#db path
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "tickets.db"
#json files path
_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

def _resolve_db_path(db_path: Path | str | None) -> Path | str:
    """Priority: explicit db_path arg > DB_PATH env var > Module default"""
    return db_path or os.environ.get("DB_PATH") or DEFAULT_DB_PATH

def _resolve_data_dir() -> Path:
    """Priority: DATA_DIR env > Module default"""
    return Path(os.environ.get("DATA_DIR") or _DATA_DIR)

# connect to the db
def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(_resolve_db_path(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON") # PRAGMA - sqlite3 way of saying, no DDL no DML, just config the engine
    return conn

# init of the db - create all our tables
def init_db(db_path: Path | str | None = None) -> None:
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8")) # This will read our schema file and execute the DDL.
        conn.commit()
    finally:
        conn.close()

# seeding of the db
def seed_from_json(db_path: Path | str | None = None) -> tuple[int, int]:
    data_dir = _resolve_data_dir()
    customers = json.loads((data_dir / "customers.json").read_text(encoding="utf-8"))
    tickets = json.loads((data_dir / "tickets.json").read_text(encoding="utf-8"))
    conn = connect(db_path)
    try:
        # Insert statement for all the data in customers.json, make a row - many times
        conn.executemany( 
            """INSERT OR REPLACE INTO customers
            (id, name, tenant, plan, primary_contact_email, created_at)
            VALUES (:id, :name, :tenant, :plan, :primary_contact_email, :created_at)""",
            customers
        )
        # Insert statement for all the data in tickets.json
        conn.executemany( # not going to duplicate seed, its going to upsert (insert/update)
            """INSERT OR REPLACE INTO tickets
            (id, title, body, priority, status, category, tenant,
            customer_id, assignee, channel, tags, created_at, updated_at)
            VALUES (:id, :title, :body, :priority, :status, :category, :tenant,
            :customer_id, :assignee, :channel, :tags, :created_at, :updated_at)""", # :key - parameter binding ?
            [ {**t, "tags": json.dumps(t.get("tags", []))} for t in tickets]
        )
        conn.commit()
    finally:
        conn.close()
    return len(customers), len(tickets)