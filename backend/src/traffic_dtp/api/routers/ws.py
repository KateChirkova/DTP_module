import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from src.traffic_dtp.api.deps import get_user_for_ws_token
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services.ws_manager import manager

router = APIRouter(prefix="/api/v1", tags=["ws"])


# keepalive ping; токен в query — как у Bearer REST
@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        user = get_user_for_ws_token(token, db)
    except Exception:
        logger.warning("WebSocket connection rejected: invalid or expired token")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.login)

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_text('{"type": "ping"}')
            except WebSocketDisconnect:
                break
    finally:
        manager.disconnect(websocket)
