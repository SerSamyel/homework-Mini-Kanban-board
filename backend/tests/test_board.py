def test_get_board_returns_three_seeded_columns(client):
    resp = client.get("/api/board")
    assert resp.status_code == 200
    data = resp.json()
    assert [c["name"] for c in data["columns"]] == ["To Do", "In Progress", "Done"]


def test_get_board_has_five_seed_tasks(client):
    resp = client.get("/api/board")
    total = sum(len(c["tasks"]) for c in resp.json()["columns"])
    assert total == 5


def test_tasks_within_column_sorted_by_position(client):
    resp = client.get("/api/board")
    in_progress = next(c for c in resp.json()["columns"] if c["id"] == 2)
    positions = [t["position"] for t in in_progress["tasks"]]
    assert positions == sorted(positions)


def test_board_requires_no_auth(client):
    # No Authorization header sent at all — must still succeed (MVP has no auth).
    resp = client.get("/api/board")
    assert resp.status_code == 200


def test_list_columns_has_no_tasks_field(client):
    resp = client.get("/api/columns")
    assert resp.status_code == 200
    data = resp.json()
    assert [c["name"] for c in data] == ["To Do", "In Progress", "Done"]
    assert all("tasks" not in c for c in data)
