import os
import sys
from pathlib import Path

# Point the store at an in-memory SQLite DB *before* app.db is imported
# anywhere, so test runs never touch the dev kanban.db file on disk.
os.environ.setdefault("KANBAN_DB_URL", "sqlite:///:memory:")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.main import app  # noqa: E402
from app.store import store  # noqa: E402


@pytest.fixture(autouse=True)
def reset_store():
    """Every test starts from the same freshly-seeded 5 tasks."""
    store.reset()
    yield


@pytest.fixture
def client():
    return TestClient(app)
