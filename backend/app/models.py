"""Pydantic schemas mirroring the shapes defined in openapi.yaml."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class Task(BaseModel):
    id: int
    title: str
    description: str
    column_id: int
    position: int
    created_at: datetime
    updated_at: datetime


class Column(BaseModel):
    id: int
    name: str
    order: int
    tasks: list[Task]


class ColumnSummary(BaseModel):
    """Column without its tasks — GET /api/columns."""

    id: int
    name: str
    order: int


class Board(BaseModel):
    columns: list[Column]


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    column_id: int


class TaskUpdateRequest(BaseModel):
    """PATCH body — every field optional, but at least one must be set."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    column_id: int | None = None
    position: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _at_least_one_field(self) -> "TaskUpdateRequest":
        if all(
            getattr(self, f) is None
            for f in ("title", "description", "column_id", "position")
        ):
            raise ValueError("at least one field must be provided")
        return self


class ErrorDetail(BaseModel):
    detail: str
