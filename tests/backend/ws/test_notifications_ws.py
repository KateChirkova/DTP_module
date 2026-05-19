# тесты WebSocket /api/v1/ws/notifications
import pytest
from starlette.websockets import WebSocketDisconnect


def test_websocket_missing_token_closes(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/ws/notifications"):
            pass


def test_websocket_invalid_token_closes(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/ws/notifications?token=invalid-token"):
            pass


def test_websocket_connect_with_valid_token(client, auth_token):
    with client.websocket_connect(
        f"/api/v1/ws/notifications?token={auth_token}"
    ) as websocket:
        websocket.send_text("ping")
