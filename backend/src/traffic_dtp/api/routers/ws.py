from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from fastapi import Query

router = APIRouter(prefix="/api/v1", tags=["ws"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WS: {len(self.active_connections)} подключений")

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [c for c in self.active_connections if c != websocket]
        print(f"WS: {len(self.active_connections)} подключений")

    async def broadcast(self, message: dict):
        dead = []
        msg_str = json.dumps(message, ensure_ascii=False)
        print(f"📡 WS Broadcast: {msg_str}")
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(msg_str)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(alias="token", default="guest")  # ← ДОБАВЬТЕ!
):
    print(f"WS token OK: {token}")  # тест
    await manager.connect(websocket)
    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_text('{"type": "ping"}')
                continue
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS error: {e}")
        manager.disconnect(websocket)