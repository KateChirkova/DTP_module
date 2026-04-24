import pytest
from fastapi.testclient import TestClient
from src.traffic_dtp.main import app

client = TestClient(app)

def test_detections_new_accident(test_db):  # pytest fixture
    response = client.post("/api/v1/detections", json={
        "screenshot_path": "tests/mock_screenshot.jpg"
    })
    assert response.status_code == 200
    assert "new_accidents" in response.json()
