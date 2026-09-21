/**
 * Real API client for the Boardly backend (see ../../backend, ../../openapi.yaml).
 *
 * Talks to http://localhost:8000/api by default. Override by setting
 * `window.KANBAN_API_BASE` in index.html before this script loads, if the
 * backend runs somewhere else.
 *
 * Same method names/shapes as the earlier localStorage mock, so app.js
 * needed no changes when this file was swapped in.
 */
(function (global) {
  const API_BASE = global.KANBAN_API_BASE || 'http://localhost:8000/api';

  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
    } catch (err) {
      const wrapped = new Error(
        `Не удалось связаться с backend (${API_BASE}). Он запущен? (${err.message})`
      );
      wrapped.cause = err;
      throw wrapped;
    }

    if (response.status === 204) return null;

    let body = null;
    try {
      body = await response.json();
    } catch {
      // No JSON body — fine for some error responses.
    }

    if (!response.ok) {
      const err = new Error((body && body.detail) || response.statusText);
      err.status = response.status;
      err.body = body;
      throw err;
    }

    return body;
  }

  const api = {
    /** GET /api/board */
    getBoard() {
      return request('/board');
    },

    /** POST /api/tasks — {title, description?, column_id} */
    createTask({ title, description = '', column_id }) {
      return request('/tasks', {
        method: 'POST',
        body: JSON.stringify({ title, description, column_id }),
      });
    },

    /** PATCH /api/tasks/{id} — any of title, description, column_id, position */
    updateTask(id, patch) {
      return request(`/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(patch),
      });
    },

    /** DELETE /api/tasks/{id} */
    deleteTask(id) {
      return request(`/tasks/${id}`, { method: 'DELETE' });
    },
  };

  global.kanbanApi = api;
})(window);
