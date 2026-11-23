import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_create_and_get_note():
    payload = {"title": "Test Note", "description": "Sample note body", "source_name": "cli"}
    create_res = client.post("/items/notes", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == "Test Note"
    assert created["content_type"] == "note"
    assert created["processing_status"] == "READY"

    get_res = client.get(f"/items/{created["id"]}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == created["id"]


def test_upload_process_and_tag_file():
    up = client.post(
        "/items/files",
        files={"file": ("pytest_doc.txt", b"Pytest extracted content", "text/plain")},
        data={"title": "Pytest Doc"},
    )
    assert up.status_code == 201
    item = up.json()
    assert item["checksum"] is not None
    assert item["processing_status"] == "PENDING"

    proc = client.post(f"/items/{item["id"]}/process")
    assert proc.status_code == 200
    assert proc.json()["processing_status"] == "READY"
    assert "Pytest extracted content" in (proc.json()["description"] or "")

    tagged = client.post(f"/items/{item["id"]}/tags", json={"tags": ["pytest", "docs"]})
    assert tagged.status_code == 200
    assert "pytest" in [t["name"] for t in tagged.json()]

    filtered = client.get("/items", params={"tag": "pytest"})
    assert filtered.status_code == 200
    assert any(x["id"] == item["id"] for x in filtered.json())


def test_process_invalid_link_marks_failed():
    lnk = client.post("/items/links", json={"url": "bad-url"})
    assert lnk.status_code == 201
    link_id = lnk.json()["id"]
    proc = client.post(f"/items/{link_id}/process")
    assert proc.status_code == 200
    assert proc.json()["processing_status"] == "FAILED"
    assert proc.json()["processing_error"] is not None


def test_stats_endpoint():
    res = client.get("/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_items" in data
    assert "total_tags" in data
    assert "by_status" in data


def test_update_and_delete_item():
    created = client.post("/items/notes", json={"title": "Temp Note"}).json()
    item_id = created["id"]
    upd = client.patch(f"/items/{item_id}", json={"title": "Renamed Note"})
    assert upd.status_code == 200
    assert upd.json()["title"] == "Renamed Note"
    dele = client.delete(f"/items/{item_id}")
    assert dele.status_code == 204
    after = client.get(f"/items/{item_id}")
    assert after.status_code == 404
