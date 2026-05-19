import logging
import os
import time

from fastapi import Depends, FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.traffic_dtp.api.routers.accidents import router as accidents_router
from src.traffic_dtp.api.routers.admin import router as admin_router
from src.traffic_dtp.api.routers.auth import router as auth_router
from src.traffic_dtp.api.routers.detections import router as detections_router
from src.traffic_dtp.api.routers.notifications import router as notifications_router
from src.traffic_dtp.api.routers.ws import router as ws_router
from src.traffic_dtp.db.session import get_db

app = FastAPI(
    title="Traffic Krasnodar DTP API",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    description=(
        "### Авторизация в Swagger\n"
        "1. **POST /api/v1/auth/login** — логин и пароль.\n"
        "2. Скопируйте **`token`** из ответа.\n"
        "3. **Authorize** -> вставьте token (без `Bearer`).\n\n"
        "### Внутренние вызовы\n"
        "- **POST /api/v1/detections** — заголовок `X-Internal-Key` (значение `DTP_INTERNAL_API_KEY` из `.env`).\n"
        "- **GET /api/v1/accidents** — как у остальных пользовательских эндпоинтов, нужен Bearer token.\n\n"
        "### Админ\n"
        "- **GET /api/v1/admin/sessions** — сессии за сутки (или `?hours=48`).\n"
        "- Нужен пользователь с **`is_admin=true`** в БД.\n"
    ),
    swagger_ui_parameters={"persistAuthorization": True},
)

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
app.include_router(admin_router)
app.include_router(ws_router)


# миграции схемы, bootstrap-пользователь, прогрев YOLO
@app.on_event("startup")
async def startup():
    from src.traffic_dtp.db.schema_migrate import (
        ensure_shared_notifications_schema,
        ensure_user_is_admin_column,
    )
    from src.traffic_dtp.db.session import engine

    ensure_user_is_admin_column(engine)
    ensure_shared_notifications_schema(engine)

    from src.traffic_dtp.services.user_bootstrap import bootstrap_user_from_env

    bootstrap_user_from_env()

    import asyncio

    from src.traffic_dtp.services.yolo_service import warmup_yolo_model

    try:
        await asyncio.to_thread(warmup_yolo_model)
        print("YOLO: модель загружена при старте")
    except Exception as e:
        print(f"YOLO: прогрев пропущен ({e})")

    print("БД готова + routers подключены!")


@app.get("/")
def root():
    return {"message": "DTP API v2.0", "status": "ok"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    metrics = {"status": "healthy", "timestamp": time.time(), "database": {}}

    try:
        tables = [
            row[0]
            for row in db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            ).fetchall()
        ]
        metrics["database"]["tables"] = tables

        key_tables = {
            "detections": "SELECT COUNT(*) FROM detections",
            "accidents": "SELECT COUNT(*) FROM accidents WHERE is_active=1",
            "notifications": (
                "SELECT COUNT(*) FROM notifications n "
                "JOIN accidents a ON a.id = n.accident_id AND a.is_active = 1"
            ),
        }

        for table, query in key_tables.items():
            if table in tables:
                count = db.execute(text(query)).scalar()
                metrics["database"][table] = {"exists": True, "count": count}

        return metrics
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

