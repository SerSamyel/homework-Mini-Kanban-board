"""SQLAlchemy ORM tables — the actual SQLite schema.

Kept separate from app/models.py (the Pydantic API schemas) on purpose:
these two shouldn't be conflated, even though their fields largely overlap.
"""
from __future__ import annotations

from sqlalchemy import Column as SAColumn
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class ColumnORM(Base):
    __tablename__ = "columns"

    id = SAColumn(Integer, primary_key=True)
    name = SAColumn(String, nullable=False)
    order = SAColumn(Integer, nullable=False)

    tasks = relationship(
        "TaskORM", back_populates="column", order_by="TaskORM.position"
    )


class TaskORM(Base):
    __tablename__ = "tasks"

    id = SAColumn(Integer, primary_key=True)
    title = SAColumn(String(200), nullable=False)
    description = SAColumn(String, nullable=False, default="")
    column_id = SAColumn(Integer, ForeignKey("columns.id"), nullable=False)
    position = SAColumn(Integer, nullable=False)
    created_at = SAColumn(DateTime(timezone=True), nullable=False)
    updated_at = SAColumn(DateTime(timezone=True), nullable=False)

    column = relationship("ColumnORM", back_populates="tasks")
