"""Shared pytest fixtures"""
import json
from pathlib import Path
import pytest

@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"

@pytest.fixture(scope="session")
def seed_tickets(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "tickets.json").read_text(encoding="utf-8"))