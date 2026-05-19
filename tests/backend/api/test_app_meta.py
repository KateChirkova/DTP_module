# тесты / и /health
def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert "message" in body


def test_health_returns_metrics(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data


def test_openapi_schema(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec.get("openapi", "").startswith("3.")
    paths = spec.get("paths", {})
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/notifications" in paths
    assert "/api/v1/accidents" in paths


def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200
