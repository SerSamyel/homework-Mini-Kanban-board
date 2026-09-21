# AGENTS.md

Instructions for AI coding agents working in this repository (Boardly — mini kanban board, AI Dev Tools Zoomcamp homework 2).

## Project shape

- `frontend/` — static HTML/CSS/vanilla JS, no build step. `js/api.js` is the *only* place that talks to the backend (`fetch` calls); `js/app.js` never calls `fetch` directly. See `frontend/README.md`.
- `backend/` — FastAPI, dependencies managed with `uv` (not pip/poetry — see `backend/pyproject.toml`). SQLite via SQLAlchemy (`backend/app/db.py`, `backend/app/db_models.py`); the actual data-access layer routers use is `backend/app/store.py` — keep its public function signatures stable so the storage backend can be swapped without touching routers.
- `openapi.yaml` (repo root) — the source of truth for the API contract. If you change an endpoint's request/response shape in the backend, update this file in the same change, and vice versa.
- `_docs/plan.md` — the original MVP spec. If a change meaningfully diverges from it (new endpoints, changed storage, changed scope), update this file too, or note the divergence in the PR/commit message.

## Running things

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000   # backend on :8000
cd frontend && python3 -m http.server 5500                                  # frontend on :5500
cd backend && uv run pytest                                                 # tests
```

## Conventions

- No authentication anywhere in this MVP (single user, no accounts) — `openapi.yaml` marks every endpoint `security: []` on purpose. Don't add auth without updating `openapi.yaml` and `_docs/plan.md` first and confirming with the project owner — it's a deliberate scope decision, not an oversight.
- Columns are fixed ("To Do", "In Progress", "Done"), seeded server-side, not user-editable in this version.
- Keep `frontend/js/api.js`'s method names and argument shapes (`getBoard`, `createTask`, `updateTask`, `deleteTask`) stable — `app.js` depends on them and previously worked unchanged across a full swap from a localStorage mock to the real backend.

## Git

- Prefer small, descriptive commits over one giant one when doing multi-step work.
- Don't force-push or rewrite history on shared branches.
- Run `uv run pytest` (backend) before committing backend changes when the dependencies are installed.
