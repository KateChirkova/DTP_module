from src.traffic_dtp.db.models import Notification

def test_get_notifications_empty(client):
    response = client.get("/api/v1/notifications?status=unread&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total"] == 0
    assert data["unread_count"] == 0

def test_mark_notification_read(client, db_session):
    n = Notification(
        accident_id=1,
        event="newaccident",
        accident_status="active",
        status="unread",
        is_sent=False,
    )
    db_session.add(n)
    db_session.commit()

    response = client.put(f"/api/v1/notifications/{n.id}/read")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "read"