# routers/detections.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.traffic_dtp.db.models import Detection, Accident
from sqlalchemy.orm import Session
from src.traffic_dtp.db.session import get_db
from typing import List
from pathlib import Path
import json
from src.traffic_dtp.services.yolo_predict import predict_accident # subprocess
from src.traffic_dtp.services.accident_processor import process_screenshot_detections
manager = None

router = APIRouter(prefix="/api", tags=["detections"])


class ScreenshotPath(BaseModel):
    screenshot_path: str # "data/screenshots/1234567890.png"


@router.post("/v1/detections")
async def process_screenshot(request: ScreenshotPath, db: Session = Depends(get_db)):
    screenshot_path = Path(request.screenshot_path)

    print(f"📁 Screenshot: {screenshot_path}")

    if not screenshot_path.exists():
        raise HTTPException(404, f"Скриншот не найден: {screenshot_path}")

    # YOLO
    print("Запуск YOLO")
    yolo_result = predict_accident(str(screenshot_path))
    print(f"YOLO РЕЗУЛЬТАТ: {yolo_result}")


    detections = yolo_result.get("detections", [])
    print(f"Детекций найдено: {len(detections)}") # Лог 4

    if not detections:
        return {
        "success": True,
        "message": "YOLO не нашёл ДТП",
        "yolo_raw": yolo_result,
        "detections": 0
        }

# Processor
    print("Обработка accidents") # Лог 5
    result = process_screenshot_detections(db, detections)
    print(f"PROCESSOR РЕЗУЛЬТАТ: {result}") # Лог 6

# WS (только если есть новые)
    for acc_id in result.get("new_accidents", []):
        print(f"NEW accident #{acc_id}")
    #await manager.broadcast({"event": "newaccident", "data": {"id": acc_id}})

    return {
        "success": True,
        "screenshot": str(screenshot_path),
        "detections_found": len(detections),
        "yolo_sample": detections[0] if detections else None, # Первая детекция
        **result
}