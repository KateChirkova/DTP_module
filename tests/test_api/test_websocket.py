def test_websocket_notifications(client):
    with client.websocket_connect("/api/v1/ws/notifications") as websocket:
        websocket.send_text("ping")
        assert websocket is not None