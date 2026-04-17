from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from typing import List, Dict
from src.traffic_dtp.db.models import Accident, Detection


def calculate_iou(box1: List[int], box2: List[int]) -> float:
    # IoU [x1,y1,x2,y2]
    x1, y1 = max(box1[0], box2[0]), max(box1[1], box2[1])
    x2, y2 = min(box1[2], box2[2]), min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1, area2 = (box1[2] - box1[0]) * (box1[3] - box1[1]), (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter / (area1 + area2 - inter) if (area1 + area2 - inter) > 0 else 0


def process_screenshot_detections(
        db: Session,
        detections: List[Dict]
) -> Dict[str, List[int]]:
    # Обработка массива (обрабатывает все на скриншоте)
    now = datetime.utcnow()
    new_accidents = []
    updated_accidents = []


    new_detections = []
    for det_data in detections:
        detection = Detection(
            confidence=det_data["confidence"],
            bbox_x1=det_data["bbox_x1"],
            bbox_y1=det_data["bbox_y1"],
            bbox_x2=det_data["bbox_x2"],
            bbox_y2=det_data["bbox_y2"]
        )
        db.add(detection)
        new_detections.append(detection)

    db.flush()  # Получаем ID detections

    # Сравниваем ДТП
    active_accidents = db.query(Accident).filter(
        Accident.status == "active",
        Accident.is_active == True
    ).all()

    matched_accident_ids = set()

    for detection in new_detections:
        bbox_det = [detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2]

        matching_accident = None
        for accident in active_accidents:
            bbox_acc = [accident.bbox_x1, accident.bbox_y1, accident.bbox_x2, accident.bbox_y2]
            if calculate_iou(bbox_det, bbox_acc) > 0.5:
                matching_accident = accident
                break

        if matching_accident:
            # UPDATE accident
            matching_accident.last_seen = now
            matching_accident.confidence = max(matching_accident.confidence, detection.confidence)
            matching_accident.status_updated_at = now
            matching_accident.missed_screenshots = 0
            detection.accident_id = matching_accident.id
            matched_accident_ids.add(matching_accident.id)
            updated_accidents.append(matching_accident.id)
        else:
            # NEW accident
            new_accident = Accident(
                bbox_x1=detection.bbox_x1, bbox_y1=detection.bbox_y1,
                bbox_x2=detection.bbox_x2, bbox_y2=detection.bbox_y2,
                confidence=detection.confidence,
                first_seen=now, last_seen=now,
                status="active", is_active=True,
                missed_screenshots=0
            )
            db.add(new_accident)
            db.flush()
            detection.accident_id = new_accident.id
            new_accidents.append(new_accident.id)

    # 3. Resolve accidents
    unmatched_accidents = []
    for accident in active_accidents:
        if accident.id not in matched_accident_ids:
            accident.missed_screenshots += 1
            accident.status_updated_at = now
            if accident.missed_screenshots >= 2:
                accident.status = "resolved"
                accident.is_active = False
                accident.resolved_at = now
                unmatched_accidents.append(accident.id)

    db.commit()

    return {
        "new_accidents": new_accidents,
        "updated_accidents": updated_accidents,
        "resolved_accidents": unmatched_accidents
    }