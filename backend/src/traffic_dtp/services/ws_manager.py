# in-memory WebSocket: один сокет на пользователя
import json
import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_login: str):
        await websocket.accept()
        self.active_connections[user_login] = websocket

    def disconnect(self, websocket: WebSocket):
        for user_login, conn in list(self.active_connections.items()):
            if conn == websocket:
                del self.active_connections[user_login]
                break

    async def broadcast_to_all(self, message: dict):
        dead = []
        for user_login, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                logger.warning(
                    "WebSocket broadcast failed for user=%s event=%s",
                    user_login,
                    message.get("event"),
                    exc_info=True,
                )
                dead.append(user_login)
        for user_login in dead:
            del self.active_connections[user_login]

    async def send_to_user(self, user_login: str, message: dict):
        connection = self.active_connections.get(user_login)
        if not connection:
            return
        try:
            await connection.send_text(json.dumps(message))
        except Exception:
            logger.warning(
                "WebSocket send failed for user=%s event=%s",
                user_login,
                message.get("event"),
                exc_info=True,
            )
            self.active_connections.pop(user_login, None)


manager = ConnectionManager()
