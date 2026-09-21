def test_create_task_appends_to_end_of_column(client):
    resp = client.post("/api/tasks", json={"title": "New task", "column_id": 1})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New task"
    assert body["column_id"] == 1
    assert body["position"] == 2  # after the 2 seeded "To Do" tasks
    assert body["description"] == ""
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_create_task_requires_title(client):
    resp = client.post("/api/tasks", json={"title": "", "column_id": 1})
    assert resp.status_code == 422


def test_create_task_requires_column_id(client):
    resp = client.post("/api/tasks", json={"title": "X"})
    assert resp.status_code == 422


def test_create_task_rejects_unknown_column(client):
    resp = client.post("/api/tasks", json={"title": "X", "column_id": 999})
    assert resp.status_code == 422


def test_update_task_changes_title(client):
    resp = client.patch("/api/tasks/1", json={"title": "Renamed"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Renamed"


def test_update_task_moves_between_columns(client):
    resp = client.patch("/api/tasks/1", json={"column_id": 2, "position": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["column_id"] == 2
    assert body["position"] == 0


def test_update_missing_task_returns_404(client):
    resp = client.patch("/api/tasks/999", json={"title": "X"})
    assert resp.status_code == 404


def test_update_unknown_column_returns_422(client):
    resp = client.patch("/api/tasks/1", json={"column_id": 999})
    assert resp.status_code == 422


def test_update_requires_at_least_one_field(client):
    resp = client.patch("/api/tasks/1", json={})
    assert resp.status_code == 422


def test_delete_task(client):
    resp = client.delete("/api/tasks/1")
    assert resp.status_code == 204

    board = client.get("/api/board").json()
    all_ids = [t["id"] for c in board["columns"] for t in c["tasks"]]
    assert 1 not in all_ids


def test_delete_missing_task_returns_404(client):
    resp = client.delete("/api/tasks/999")
    assert resp.status_code == 404


def test_tasks_endpoints_require_no_auth(client):
    resp = client.post("/api/tasks", json={"title": "No auth needed", "column_id": 1})
    assert resp.status_code == 201


def test_get_task_by_id(client):
    resp = client.get("/api/tasks/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_get_missing_task_returns_404(client):
    resp = client.get("/api/tasks/999")
    assert resp.status_code == 404
