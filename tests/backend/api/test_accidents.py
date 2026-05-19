# тесты GET /api/v1/accidents
from datetime import datetime, timezone

import pytest

from src.traffic_dtp.db.models import Accident


def test_accidents_requires_auth(client):
    r = client.get("/api/v1/accidents")
    assert r.status_code == 401


def test_accidents_empty_list(client, auth_headers):
    r = client.get("/api/v1/accidents", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] == 0
    assert data["accidents"] == []


def test_accidents_limit_respected(client, db_session, auth_headers):
    now = datetime.now(timezone.utc)
    for i in range(3):
        db_session.add(
            Accident(
                bbox_x1=i,
                bbox_y1=0,
                bbox_x2=i + 5,
                bbox_y2=5,
                confidence=0.5,
                first_seen=now,
                last_seen=now,
                event_status="new",
                is_active=True,
                missed_screenshots=0,
            )
        )
    db_session.commit()

    r = client.get("/api/v1/accidents?limit=2&status=all", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["count"] == 2


@pytest.mark.parametrize(
    "query",
    [
        "limit=0",
        "limit=101",
        "status=invalid_status",
    ],
)
def test_accidents_query_validation_422(client, auth_headers, query):
    r = client.get(f"/api/v1/accidents?{query}", headers=auth_headers)
    assert r.status_code == 422


def test_accidents_status_all_includes_active_and_resolved(client, db_session, auth_headers):
    now = datetime.now(timezone.utc)
    db_session.add(
        Accident(
            bbox_x1=0,
            bbox_y1=0,
            bbox_x2=10,
            bbox_y2=10,
            confidence=0.9,
            first_seen=now,
            last_seen=now,
            event_status="resolved",
            is_active=False,
            missed_screenshots=2,
        )
    )
    db_session.add(
        Accident(
            bbox_x1=20,
            bbox_y1=20,
            bbox_x2=30,
            bbox_y2=30,
            confidence=0.8,
            first_seen=now,
            last_seen=now,
            event_status="new",
            is_active=True,
            missed_screenshots=0,
        )
    )
    db_session.commit()

    r = client.get("/api/v1/accidents?status=all", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["count"] == 2
    statuses = {a["status"] for a in r.json()["accidents"]}
    assert statuses == {"new", "resolved"}

    r_default = client.get("/api/v1/accidents", headers=auth_headers)
    assert r_default.status_code == 200
    assert r_default.json()["count"] == 2


def test_accidents_filter_status_new(client, db_session, auth_headers):
    now = datetime.now(timezone.utc)
    db_session.add(
        Accident(
            bbox_x1=0,
            bbox_y1=0,
            bbox_x2=5,
            bbox_y2=5,
            confidence=0.9,
            first_seen=now,
            last_seen=now,
            event_status="new",
            is_active=True,
            missed_screenshots=0,
        )
    )
    db_session.add(
        Accident(
            bbox_x1=10,
            bbox_y1=10,
            bbox_x2=20,
            bbox_y2=20,
            confidence=0.8,
            first_seen=now,
            last_seen=now,
            event_status="updated",
            is_active=True,
            missed_screenshots=0,
        )
    )
    db_session.commit()

    r = client.get("/api/v1/accidents?status=new", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["count"] == 1
    assert r.json()["accidents"][0]["status"] == "new"
