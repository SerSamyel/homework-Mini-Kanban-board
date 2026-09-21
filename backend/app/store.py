"""Data store backed by SQLite via SQLAlchemy (see app/db.py, app/db_models.py).

Public functions (get_board, create_task, get_task, update_task,
delete_task, reset) are unchanged from the earlier in-memory-dict version —
routers are untouched by this swap.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .db import Base, SessionLocal, engine
from .db_models import ColumnORM, TaskORM


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id


class UnknownColumnError(Exception):
    def __init__(self, column_id: int):
        super().__init__(f"Unknown column_id {column_id}")
        self.column_id = column_id


COLUMNS: list[dict[str, Any]] = [
    {"id": 1, "name": "To Do", "order": 0},
    {"id": 2, "name": "In Progress", "order": 1},
    {"id": 3, "name": "Done", "order": 2},
]
_COLUMN_IDS = {c["id"] for c in COLUMNS}

_SEED_TASKS: list[dict[str, Any]] = [
    {"title": "Спроектировать модель данных", "description": "Board/Column/Task, см. _docs/plan.md", "column_id": 3},
    {"title": "Сделать API на FastAPI", "description": "GET/POST/PATCH/DELETE для задач", "column_id": 2},
    {"title": "Собрать фронтенд на моках", "description": "Экран для проверки перед подключением backend", "column_id": 2},
    {"title": "Подключить реальный backend", "description": "", "column_id": 1},
    {"title": "Задеплоить приложение", "description": "", "column_id": 1},
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _task_to_dict(task: TaskORM) -> dict[str, Any]:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "column_id": task.column_id,
        "position": task.position,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


class Store:
    """Data-access layer over a SQLite database. One session per call —
    fine at this scale, simplest thing that's correct for a single-process
    MVP."""

    def __init__(self) -> None:
        Base.metadata.create_all(bind=engine)
        self._seed_columns()
        self._seed_tasks_if_empty()

    def _seed_columns(self) -> None:
        with SessionLocal() as session:
            if session.query(ColumnORM).count() == 0:
                session.add_all(ColumnORM(**c) for c in COLUMNS)
                session.commit()

    def _seed_tasks_if_empty(self) -> None:
        with SessionLocal() as session:
            if session.query(TaskORM).count() == 0:
                self._insert_seed_tasks(session)
                session.commit()

    def _insert_seed_tasks(self, session) -> None:
        counters = {c["id"]: 0 for c in COLUMNS}
        for data in _SEED_TASKS:
            now = _now()
            pos = counters[data["column_id"]]
            counters[data["column_id"]] += 1
            session.add(
                TaskORM(
                    title=data["title"],
                    description=data["description"],
                    column_id=data["column_id"],
                    position=pos,
                    created_at=now,
                    updated_at=now,
                )
            )

    def reset(self) -> None:
        """Used by tests: wipe tasks and reseed. Columns are left as-is."""
        with SessionLocal() as session:
            session.query(TaskORM).delete()
            session.commit()
            self._insert_seed_tasks(session)
            session.commit()

    def _next_position(self, session, column_id: int) -> int:
        return session.query(TaskORM).filter_by(column_id=column_id).count()

    def get_columns(self) -> list[dict[str, Any]]:
        """Columns only, no tasks — backs GET /api/columns."""
        with SessionLocal() as session:
            rows = session.query(ColumnORM).order_by(ColumnORM.order).all()
            return [{"id": c.id, "name": c.name, "order": c.order} for c in rows]

    def get_board(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            columns = []
            for col in COLUMNS:
                tasks = (
                    session.query(TaskORM)
                    .filter_by(column_id=col["id"])
                    .order_by(TaskORM.position)
                    .all()
                )
                columns.append({**col, "tasks": [_task_to_dict(t) for t in tasks]})
            return columns

    def create_task(self, *, title: str, description: str = "", column_id: int) -> dict[str, Any]:
        if column_id not in _COLUMN_IDS:
            raise UnknownColumnError(column_id)
        with SessionLocal() as session:
            now = _now()
            task = TaskORM(
                title=title,
                description=description,
                column_id=column_id,
                position=self._next_position(session, column_id),
                created_at=now,
                updated_at=now,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return _task_to_dict(task)

    def get_task(self, task_id: int) -> dict[str, Any]:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            return _task_to_dict(task)

    def update_task(self, task_id: int, **changes: Any) -> dict[str, Any]:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            column_id = changes.get("column_id")
            if column_id is not None and column_id not in _COLUMN_IDS:
                raise UnknownColumnError(column_id)
            for key, value in changes.items():
                if value is not None:
                    setattr(task, key, value)
            task.updated_at = _now()
            session.commit()
            session.refresh(task)
            return _task_to_dict(task)

    def delete_task(self, task_id: int) -> None:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            session.delete(task)
            session.commit()


store = Store()
