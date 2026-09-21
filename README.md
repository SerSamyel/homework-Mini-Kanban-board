# AI Dev Tools Zoomcamp homework 2 — Boardly

**Boardly** — мини-канбан-доска: веб-приложение для одного пользователя с созданием задач и перетаскиванием их между колонками (To Do / In Progress / Done).

Спецификация — [`_docs/plan.md`](_docs/plan.md); контракт API — [`openapi.yaml`](openapi.yaml); инструкции для AI-агента — [`AGENTS.md`](AGENTS.md).

## Запуск

Backend (FastAPI + SQLite, порт 8000):

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Frontend (статика, порт 5500) — в отдельном терминале:

```bash
cd frontend
python3 -m http.server 5500
```

Открыть http://localhost:5500.

## Тесты

```bash
cd backend
uv run pytest
```

## Структура

- `frontend/` — HTML/CSS/vanilla JS, без сборки ([подробнее](frontend/README.md))
- `backend/` — FastAPI + SQLAlchemy + SQLite, управление зависимостями через uv ([подробнее](backend/README.md))
- `openapi.yaml` — контракт API между frontend и backend
- `_docs/plan.md` — спецификация MVP
