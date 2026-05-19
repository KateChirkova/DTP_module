# тесты POST /api/v1/detections (X-Internal-Key)
from src.traffic_dtp.services import paths as paths_mod


def test_detections_requires_body(client, internal_headers):
    r = client.post("/api/v1/detections", headers=internal_headers)
    assert r.status_code == 422


def test_detections_requires_internal_key(client, monkeypatch):
    monkeypatch.setenv("DTP_INTERNAL_API_KEY", "secret-key")
    r = client.post("/api/v1/detections", json={"screenshot_path": "x.jpg"})
    assert r.status_code == 403


def test_detections_invalid_json_not_object(client, internal_headers):
    r = client.post(
        "/api/v1/detections",
        content='"not-json-object"',
        headers={**internal_headers, "Content-Type": "application/json"},
    )
    assert r.status_code == 422


def test_detections_screenshot_not_found(client, tmp_path, monkeypatch, internal_headers):
    monkeypatch.setattr(paths_mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(paths_mod, "SCREENSHOTS_PATH", "shots")
    (tmp_path / "shots").mkdir(parents=True)

    r = client.post(
        "/api/v1/detections",
        json={"screenshot_path": "missing_file_xyz.jpg"},
        headers=internal_headers,
    )
    assert r.status_code == 404
    assert "не найден" in r.json()["detail"] or "not found" in r.json()["detail"].lower()


def test_detections_empty_file_no_yolo(client, tmp_path, monkeypatch, internal_headers):
    # пустой файл — без YOLO, пустые детекции
    monkeypatch.setattr(paths_mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(paths_mod, "SCREENSHOTS_PATH", "shots")
    shots = tmp_path / "shots"
    shots.mkdir(parents=True)
    (shots / "empty_frame.jpg").write_bytes(b"")

    r = client.post(
        "/api/v1/detections",
        json={"screenshot_path": "empty_frame.jpg"},
        headers=internal_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    assert body["filename"] == "empty_frame.jpg"
    assert body["detections_found"] == 0
    assert body["new_accidents"] == 0
    assert body["updated_accidents"] == 0
