# Backend — Boardly (mini kanban board)

FastAPI implementation of [`openapi.yaml`](../openapi.yaml). SQLite database via SQLAlchemy (`kanban.db`, created and seeded automatically on first run — see `app/db.py`). Single-user MVP — **no authentication on any endpoint** (see `openapi.yaml`'s `security: []`).

Dependencies are managed with [uv](https://docs.astral.sh/uv/) — no manual venv/pip.

## Structure

- `pyproject.toml` — dependencies (`uv sync` reads this; `uv.lock` pins exact versions once generated).
- `app/db.py` — SQLAlchemy engine/session setup (SQLite file by default; `KANBAN_DB_URL` env var overrides it — tests use an in-memory DB).
- `app/db_models.py` — SQLAlchemy ORM tables (`ColumnORM`, `TaskORM`) — the actual DB schema.
- `app/models.py` — Pydantic request/response schemas (mirrors `openapi.yaml` components).
- `app/store.py` — data-access layer: seeding, create/read/update/delete for tasks, on top of `app/db.py` + `app/db_models.py`. Same public function signatures regardless of what's backing it — this module is the only one routers talk to for data.
- `app/routers/board.py` — `GET /api/board`, `GET /api/columns`.
- `app/routers/tasks.py` — `POST /api/tasks`, `GET /api/tasks/{id}`, `PATCH /api/tasks/{id}`, `DELETE /api/tasks/{id}`.
- `app/main.py` — creates the `FastAPI` app, wires CORS (permissive, local-dev only) and the two routers.
- `tests/` — pytest + `TestClient`, one file per router, store reset to a fresh seed before every test (`tests/conftest.py`, in-memory SQLite so `kanban.db` is never touched by test runs).

## Run

```bash
uv sync                                    # creates backend/.venv, installs deps, writes uv.lock on first run
uv run uvicorn app.main:app --reload --port 8000
```

API is then at http://localhost:8000/api, interactive docs at http://localhost:8000/docs. `kanban.db` (SQLite file, gitignored) is created next to this README on first run.

The frontend (`../frontend`) expects the backend at exactly this address — see `KANBAN_API_BASE` in `../frontend/index.html` if you run it elsewhere.

## Test

```bash
uv run pytest
```

## Note on authentication

`openapi.yaml` marks every endpoint `security: []` — this is a deliberate MVP decision (single user, no accounts), not an oversight. If multi-user support is added later, `app/db_models.py`'s `TaskORM` would need an `owner_id` column and an `app/auth.py` module (password hashing + bearer tokens) would gate the mutating endpoints; `openapi.yaml` would need updating first since the frontend currently sends no `Authorization` header at all.
