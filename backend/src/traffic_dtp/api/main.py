from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.traffic_dtp.db.session import SessionLocal, engine, Base, get_db
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.api.routers.detections import router as detections_router  # ← ТВОЙ ROUTERS!
from typing import List
import json
from datetime import datetime
import hashlib

# WebSocket Manager
connected_clients = []


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for client in self.active_connections:
            try:
                await client.send_text(json.dumps(message))
            except:
                disconnected.append(client)
        for client in disconnected:
            self.active_connections.remove(client)


manager = ConnectionManager()

# FastAPI app
app = FastAPI(title="Traffic Krasnodar DTP API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение routers
app.include_router(detections_router)  # /api/v1/detections


# WebSocket
@app.websocket("/api/v1/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Login
@app.post("/api/v1/auth/login")
async def login(req: dict, db: Session = Depends(get_db)):  # dict вместо BaseModel
    user = db.query(User).filter(User.login == req.get("login")).first()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    password_hash = hashlib.sha256(req.get("password", "").encode()).hexdigest()

    if user.password_hash == password_hash:
        return {"success": True, "token": f"jwt-{req.get('login')}-2026", "expires_in": 86400}
    raise HTTPException(status_code=401, detail="Неверный пароль")


# Активные ДТП
@app.get("/api/v1/accidents")
async def get_accidents(db: Session = Depends(get_db), limit: int = 10):
    accidents = db.query(Detection).join(Accident).filter(
        Accident.status == "active"
    ).order_by(Detection.id.desc()).limit(limit).all()

    return {
        "success": True,
        "count": len(accidents),
        "accidents": [{
            "id": d.id,
            "confidence": round(d.confidence, 2),
            "bbox": [d.bboxx1, d.bbxy1, d.bboxx2, d.bboxy2],
            "accident_status": d.accident.status if hasattr(d, 'accident') else "unknown"
        } for d in accidents]
    }


# Health + Debug
@app.get("/")
async def root():
    return {"message": "DTP API v2.0 🚗", "detections": "api/v1/detections READY"}


@app.get("/health")
async def health():
    return {"status": "healthy", "detections_route": "WORKING"}


@app.get("/debug/routes")
async def debug_routes():
    detections_paths = [str(r.path) for r in app.routes if 'detections' in str(r.path)]
    return {
        "total_routes": len(app.routes),
        "detections_paths": detections_paths,
        "message": "Check logs for /api/v1/detections from routers!"
    }


# Startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ БД готова + routers подключены!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)