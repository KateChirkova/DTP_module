from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Dict
from types import SimpleNamespace
import json, asyncio
from sqlalchemy.orm import Session
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.api.deps import get_current_user

router = APIRouter(prefix="/api/v1", tags=["ws"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_login: str):
        await websocket.accept()
        self.active_connections[user_login] = websocket
        print(f"WS: {user_login} подключен. Всего: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        for user_login, conn in list(self.active_connections.items()):
            if conn == websocket:
                del self.active_connections[user_login]
                print(f"WS: {user_login} отключен")
                break

    async def broadcast_to_all(self, message: dict):
        dead = []
        for user_login, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(json.dumps(message))
            except:
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
            self.active_connections.pop(user_login, None)

manager = ConnectionManager()

@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        user = get_current_user(authorization=SimpleNamespace(credentials=token), db=db)
        user_login = user.login
        print(f"WS: {user_login} авторизован")
    except Exception as e:
        print(f"WS: авторизация failed: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_login)

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_text('{"type": "ping"}')
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def notify_new_accident(accident_id: int, accident_time: str):
    message = {
        "event": "newaccident",
        "data": {"id": accident_id, "created_at": accident_time, "status": "new"},
    }
    await manager.broadcast_to_all(message)
    print(f"Notification #{accident_id} -> {len(manager.active_connections)} users")