# В api/main.py → /v1/detections
from typing import Optional


def find_or_create_accident(detection: Detection, db: Session) -> Accident:
    # Поиск похожих по bbox (IoU > 0.5)
    similar = db.query(Detection).filter(
        Detection.bboxx1.between(detection.bboxx1 - 50, detection.bboxx1 + 50),
        Detection.bbxy1.between(detection.bbxy1 - 50, detection.bbxy1 + 50)
    ).all()

    for d in similar:
        iou = calculate_iou(d, detection)
        if iou > 0.5:
            accident = db.query(Accident).filter(Accident.id == d.accident_id).first()
            detection.accident_id = accident.id
            return accident

    # Новый accident
    accident = Accident(confidence=detection.confidence, bbox_center_x=(detection.bboxx1 + detection.bboxx2) / 2)
    db.add(accident)
    db.flush()
    detection.accident_id = accident.id
    accident.is_new = True
    return accident


def calculate_iou(d1: Detection, d2: Detection) -> float:
    # IoU bbox
    x1 = max(d1.bboxx1, d2.bboxx1)
    y1 = max(d1.bbxy1, d2.bbxy1)
    x2 = min(d1.bboxx2, d2.bboxx2)
    y2 = min(d1.bbxy2, d2.bbxy2)

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = (d1.bboxx2 - d1.bboxx1) * (d1.bbxy2 - d1.bbxy1) + (d2.bboxx2 - d2.bboxx1) * (d2.bbxy2 - d2.bbxy1) - inter
    return inter / union if union > 0 else 0