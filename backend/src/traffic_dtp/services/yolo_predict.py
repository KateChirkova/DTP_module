import json
from pathlib import Path
from typing import Dict, List, Optional

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "runs" / "detect" / "dtp_krasnodar_light9" / "weights" / "best.pt"

_model = None

def get_model() -> YOLO:
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Модель не найдена: {MODEL_PATH}")
        _model = YOLO(str(MODEL_PATH))
    return _model

def predict_accident(image_path: str) -> Dict:
    img_path = Path(image_path).resolve()

    if not img_path.exists():
        raise FileNotFoundError(f"Изображение не найдено: {img_path}")

    model = get_model()
    results = model.predict(source=str(img_path), verbose=False)[0]

    detections: List[Dict] = []
    if results.boxes is not None:
        for box in results.boxes:
            xyxy = box.xyxy[0].tolist()
            detections.append({
                "confidence": float(box.conf[0]) if hasattr(box.conf, "__len__") else float(box.conf),
                "bbox_x1": int(xyxy[0]),
                "bbox_y1": int(xyxy[1]),
                "bbox_x2": int(xyxy[2]),
                "bbox_y2": int(xyxy[3]),
            })

    return {
        "status": "success",
        "image_path": str(img_path),
        "total_detections": len(detections),
        "detections": detections,
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    args = parser.parse_args()

    result = predict_accident(args.image_path)
    print(json.dumps(result, ensure_ascii=False))