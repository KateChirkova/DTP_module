from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.accidents import router
from src.traffic_dtp.db.session import engine, Base

app = FastAPI(title="Traffic Krasnodar DTP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["Accidents"])

@app.on_event("startup")
async def startup():
    """Создаёт таблицы при старте"""
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "DTP API готов!"}