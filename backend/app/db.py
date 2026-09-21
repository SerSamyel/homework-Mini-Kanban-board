"""SQLAlchemy engine/session setup.

SQLite file by default (kanban.db, next to this package) — matches
_docs/plan.md ("Хранение — SQLAlchemy + SQLite"). The URL can be overridden
via the KANBAN_DB_URL env var; tests point this at an in-memory database so
test runs never touch kanban.db on disk (see tests/conftest.py).
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.environ.get("KANBAN_DB_URL", "sqlite:///./kanban.db")

_connect_args = {"check_same_thread": False}
_engine_kwargs: dict = {}
if DATABASE_URL == "sqlite:///:memory:":
    # A plain in-memory SQLite DB is per-connection; StaticPool keeps every
    # session on the same connection so the schema/data actually persist
    # for the lifetime of the test process.
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, connect_args=_connect_args, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
