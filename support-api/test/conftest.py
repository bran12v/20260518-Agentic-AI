"""Shared pytest fixtures"""
import json
import os
from pathlib import Path
from typing import Any
import pytest

import psycopg

from support_api.storage import init_db, seed_from_json

@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"

@pytest.fixture(scope="session")
def seed_tickets(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "tickets.json").read_text(encoding="utf-8"))

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Resolved the DB url once per session"""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "TEST_DATABASE_URL not set",
            allow_module_level=False
        )
    try:
        with psycopg.connect(url, connection_timout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except Exception as err:
        pytest.skip(
            f"Cannot reach TEST_DATABASE_URL: {err}",
            allow_module_level=False
        )
    return url

@pytest.fixture
def db_url(test_database_url: str) -> str:
    # drop_all(test_database_url)
    init_db(test_database_url)
    seed_from_json(test_database_url)
    return test_database_url
    # drop_all(test_database_url)