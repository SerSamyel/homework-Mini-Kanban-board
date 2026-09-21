# Frontend — Boardly (mini kanban board)

Статический фронтенд без сборки: HTML + CSS + vanilla JS, drag-and-drop через [SortableJS](https://github.com/SortableJS/Sortable) (подключается с CDN). Обращается к backend по REST API — см. `js/api.js` и [`../openapi.yaml`](../openapi.yaml).

## Запуск

Backend должен быть запущен первым (см. [`../backend/README.md`](../backend/README.md)) — по умолчанию на `http://localhost:8000`.

```bash
cd frontend
python3 -m http.server 5500
```

Открыть http://localhost:5500. Если backend поднят на другом адресе — поменять `window.KANBAN_API_BASE` в `index.html`.

## Как устроено

- `index.html` — разметка доски и модалки создания/редактирования задачи, здесь же задаётся `KANBAN_API_BASE`.
- `css/styles.css` — стили.
- `js/api.js` — клиент backend API (`fetch`): `getBoard / createTask / updateTask / deleteTask`, формы запросов/ответов совпадают с `openapi.yaml`.
- `js/app.js` — рендер доски, обработка форм, интеграция SortableJS. Обращается только к `window.kanbanApi`.

## История

Изначально `js/api.js` был мок-слоем на `localStorage` (для проверки фронтенда до появления backend) — теперь заменён на реальные `fetch`-запросы; `js/app.js` не менялся, т.к. набор методов и их сигнатуры остались те же.
