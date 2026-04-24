from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import time
import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.traffic_dtp.api.routers.ws import manager

from src.traffic_dtp.db.session import get_db

# Routers
from src.traffic_dtp.api.routers.detections import router as detections_router
from src.traffic_dtp.api.routers.notifications import router as notifications_router
from src.traffic_dtp.api.routers.ws import router as ws_router
from src.traffic_dtp.api.routers.accidents import router as accidents_router
from src.traffic_dtp.api.routers.auth import router as auth_router

load_dotenv()

app = FastAPI(
    title="Traffic Krasnodar DTP API",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detections_router)
app.include_router(notifications_router)
app.include_router(accidents_router)
app.include_router(auth_router)
app.include_router(ws_router)


@app.on_event("startup")
async def startup():
    print("✅ БД готова + routers подключены!")


@app.get("/")
async def root():
    return {"message": "DTP API v2.0 🚗", "status": "ok"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    metrics = {"status": "healthy", "timestamp": time.time(), "database": {}}

    try:
        # таблицы
        tables = [row[0] for row in db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()]
        metrics["database"]["tables"] = tables

        # Counts
        key_tables = {
            "detections": "SELECT COUNT(*) FROM detections",
            "accidents": "SELECT COUNT(*) FROM accidents WHERE is_active=1",  # Только active!
            "notifications": "SELECT COUNT(*) FROM notifications WHERE status='unread'"
        }

        for table, query in key_tables.items():
            if table in tables:
                count = db.execute(text(query)).scalar()
                metrics["database"][table] = {"exists": True, "count": count}

        db.commit()
        return metrics
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/test-ws")
async def test_broadcast():
    await manager.broadcast({
        "event": "newaccident",
        "data": {"id": 999, "status": "test"}
    })
    return {"message": "WS test broadcast sent!"}