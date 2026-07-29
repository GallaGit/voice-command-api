from fastapi.testclient import TestClient

from src.app.main import app
from src.app.services import task_store


def test_crud_and_flow() -> None:
    task_store.tasks.clear()
    task_store._next_id = 1

    client = TestClient(app)

    assert client.get("/").json() == {"status": "ok"}
    assert client.get("/tasks").json() == []

    created = client.post("/tasks", json={"title": "Buy milk"})
    assert created.status_code == 201
    assert created.json() == {"id": 1, "title": "Buy milk", "done": False}

    created2 = client.post("/tasks", json={"title": "Walk dog", "done": True})
    assert created2.status_code == 201
    assert created2.json()["id"] == 2

    patched = client.patch("/tasks/1", json={"done": True})
    assert patched.status_code == 200
    assert patched.json()["done"] is True

    replaced = client.put("/tasks/2", json={"title": "Walk the dog", "done": False})
    assert replaced.status_code == 200
    assert replaced.json()["title"] == "Walk the dog"

    deleted = client.delete("/tasks/2")
    assert deleted.status_code == 200
    assert "deleted" in deleted.json()["message"]

    missing = client.get("/tasks/999")
    # no get-by-id route; 404/405 acceptable depending on router
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404

    tasks = client.get("/tasks").json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == 1

    print("CRUD OK")


if __name__ == "__main__":
    test_crud_and_flow()
