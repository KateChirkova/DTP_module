import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from ultralytics import YOLO
from fastapi import HTTPException

# ПУТИ
MODEL_PATH = Path("../backend/src/traffic_dtp/ml/runs/detect/dtp_krasnodar_light9/weights/best.pt").resolve()
DATA_PATH = Path("../../akaito_dtp/data/screenshots").resolve()  # ← Ваши скриншоты


def predict_accident(image_path: Optional[str] = None) -> Dict:

    if image_path is None:
        images = list(DATA_PATH.glob("*.jpg")) + list(DATA_PATH.glob("*.png"))
        if not images:
            raise HTTPException(status_code=404, detail=f"Изображения не найдены в {DATA_PATH}")
        image_path = str(images[0])
    else:
        image_path = str(Path(image_path).resolve())

    if not Path(image_path).exists():
        raise HTTPException(status_code=404, detail=f"Изображение не найдено: {image_path}")
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Модель не найдена: {MODEL_PATH}")

    model = YOLO(str(MODEL_PATH))
    results = model(image_path)[0]

    detections = []  # ← МАССИВ всех ДТП!
    if results.boxes is not None:
        for box in results.boxes:
            detections.append({
                "confidence": float(box.conf),
                "bbox_x1": int(box.xyxy[0][0]),
                "bbox_y1": int(box.xyxy[0][1]),
                "bbox_x2": int(box.xyxy[0][2]),
                "bbox_y2": int(box.xyxy[0][3])
            })

    return {
        "status": "success",
        "image_path": image_path,
        "total_detections": len(detections),
        "detections": detections  # ← МАССИВ объектов!
    }