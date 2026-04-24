from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Dict

from src.traffic_dtp.db.models import Accident, Detection


def calculate_iou(box1: List[int], box2: List[int]) -> float:
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = max(0, box1[2] - box1[0]) * max(0, box1[3] - box1[1])
    area2 = max(0, box2[2] - box2[0]) * max(0, box2[3] - box2[1])

    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0


def process_screenshot_detections(db: Session, detections: List[Dict]) -> Dict[str, List[int]]:
    print(f"🔍 process_screenshot_detections: {len(detections)} detections")
    print(f"First detection: {detections[0] if detections else 'EMPTY'}")

    now = datetime.now(timezone.utc)
    new_accidents = []
    updated_accidents = []
    resolved_accidents = []

    new_detections = []
    for det_data in detections:
        print(f"Creating Detection: bbox={det_data.get('bbox_x1')}-{det_data.get('bbox_x2')}")
        detection = Detection(
            confidence=det_data["confidence"],
            bbox_x1=det_data["bbox_x1"],
            bbox_y1=det_data["bbox_y1"],
            bbox_x2=det_data["bbox_x2"],
            bbox_y2=det_data["bbox_y2"],
        )
        db.add(detection)
        new_detections.append(detection)

    db.flush()
    print(f"✅ {len(new_detections)} Detection сохранены")

    active_accidents = db.query(Accident).filter(Accident.is_active == True).all()
    print(f"Active accidents: {len(active_accidents)}")

    matched_accident_ids = set()

    for detection in new_detections:
        bbox_det = [detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2]
        print(f"🔎 Matching bbox: {bbox_det}")

        matching_accident = None
        for accident in active_accidents:
            bbox_acc = [accident.bbox_x1, accident.bbox_y1, accident.bbox_x2, accident.bbox_y2]
            iou = calculate_iou(bbox_det, bbox_acc)
            print(f"IoU with accident {accident.id}: {iou:.2f}")
            if iou > 0.5:
                matching_accident = accident
                break

        if matching_accident:
            print(f"✅ Match accident {matching_accident.id}")
            matching_accident.last_seen = now
            matching_accident.confidence = max(matching_accident.confidence or 0, detection.confidence)
            matching_accident.status_updated_at = now
            matching_accident.missed_screenshots = 0
            matching_accident.event_status = "updated"
            detection.accident_id = matching_accident.id
            matched_accident_ids.add(matching_accident.id)
            updated_accidents.append(matching_accident.id)
        else:
            print("➕ Creating NEW accident")
            new_accident = Accident(
                bbox_x1=detection.bbox_x1, bbox_y1=detection.bbox_y1,
                bbox_x2=detection.bbox_x2, bbox_y2=detection.bbox_y2,
                confidence=detection.confidence,
                first_seen=now, last_seen=now,
                event_status="created", is_active=True,
                missed_screenshots=0, status_updated_at=now
            )
            db.add(new_accident)
            db.flush()
            detection.accident_id = new_accident.id
            new_accidents.append(new_accident.id)
            print(f"✅ NEW accident ID: {new_accident.id}")

    for accident in active_accidents:
        if accident.id not in matched_accident_ids:
            accident.missed_screenshots += 1
            accident.status_updated_at = now
            if accident.missed_screenshots >= 2:
                accident.event_status = "resolved"
                accident.is_active = False
                accident.resolved_at = now
                resolved_accidents.append(accident.id)
                print(f"❌ Resolved accident {accident.id}")

    print(f"🎯 RESULT: NEW={new_accidents} UPDATED={updated_accidents} RESOLVED={resolved_accidents}")
    return {
        "new_accidents": new_accidents,
        "updated_accidents": updated_accidents,
        "resolved_accidents": resolved_accidents,
    }