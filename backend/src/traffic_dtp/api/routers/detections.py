from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path
import os
from dotenv import load_dotenv

from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.services.yolo_service import predict_accident
from src.traffic_dtp.services.accident_processor import process_screenshot_detections
from src.traffic_dtp.services.notifications import create_notification
from src.traffic_dtp.api.routers.ws import manager  # ✅ Broadcast

load_dotenv()

router = APIRouter(prefix="/api", tags=["detections"])
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "."))
SCREENSHOTS_PATH = os.getenv("SCREENSHOTS_PATH", "data/screenshots")


class ScreenshotPath(BaseModel):
    screenshot_path: str


@router.post("/v1/detections")
async def process_screenshot(request: ScreenshotPath, db: Session = Depends(get_db)):
    screenshot_path = request.screenshot_path.replace("\\", "/")
    filename = Path(screenshot_path).name
    relative_path = f"{SCREENSHOTS_PATH}/{filename}" if not screenshot_path.startswith(
        SCREENSHOTS_PATH) else screenshot_path
    full_path = PROJECT_ROOT / relative_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Скриншот '{filename}' не найден: {full_path}")

    print(f"📸 Processing: {full_path}")

    # ✅ YOLO предсказание
    yolo_result = predict_accident(str(full_path))
    detections = yolo_result.get("detections", [])
    print(f"YOLO found {len(detections)} detections")

    if not detections:
        return {
            "success": True,
            "message": "YOLO не нашёл ДТП",
            "detections_found": 0,
            "filename": filename
        }

    result = process_screenshot_detections(db, detections)
    print(f"🚀 NEW={result.get('new_accidents', [])} UPDATED={result.get('updated_accidents', [])}")

    new_accs = result.get("new_accidents", [])
    updated_accs = result.get("updated_accidents", [])
    resolved_accs = result.get("resolved_accidents", [])

    for acc_id in new_accs + updated_accs:
        create_notification(db, acc_id)

    for acc_id in new_accs:
        await manager.broadcast({
            "event": "newaccident",
            "data": {"id": acc_id, "status": "active"}
        })
    for acc_id in updated_accs:
        await manager.broadcast({
            "event": "accidentupdated",
            "data": {"id": acc_id}
        })
    for acc_id in resolved_accs:
        await manager.broadcast({
            "event": "accidentresolved",
            "data": {"id": acc_id}
        })

    db.commit()
    return {
        "success": True,
        "filename": filename,
        "detections_found": len(detections),
        "new_accidents": len(new_accs),
        "updated_accidents": len(updated_accs),
        "resolved_accidents": len(resolved_accs)
    }