from datetime import datetime, timedelta, timezone
from typing import Dict, List

from sqlalchemy.orm import Session

from src.traffic_dtp.db.models import Accident, Detection
from src.traffic_dtp.services.notifications import delete_notifications_for_accident

# порог совпадения bbox; окно «живого» ДТП; кадров без детекции до закрытия
IOU_MATCH_THRESHOLD = 0.5
ACTIVE_WINDOW_HOURS = 12
MISSED_FRAMES_TO_RESOLVE = 2


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


def _bbox_from_detection(detection: Detection) -> List[int]:
    return [detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2]


def _bbox_from_accident(accident: Accident) -> List[int]:
    return [accident.bbox_x1, accident.bbox_y1, accident.bbox_x2, accident.bbox_y2]


def _save_detections(db: Session, detections: List[Dict]) -> List[Detection]:
    saved: List[Detection] = []
    for det_data in detections:
        detection = Detection(
            confidence=det_data["confidence"],
            bbox_x1=det_data["bbox_x1"],
            bbox_y1=det_data["bbox_y1"],
            bbox_x2=det_data["bbox_x2"],
            bbox_y2=det_data["bbox_y2"],
        )
        db.add(detection)
        saved.append(detection)
    db.flush()
    return saved


# сопоставление детекции с существующим ДТП по IoU
def _find_best_matching_accident(
    bbox_det: List[int],
    candidates: List[Accident],
) -> Accident | None:
    best_accident = None
    best_iou = 0.0
    for accident in candidates:
        iou = calculate_iou(bbox_det, _bbox_from_accident(accident))
        if iou > best_iou:
            best_iou = iou
            best_accident = accident
    if best_iou <= IOU_MATCH_THRESHOLD:
        return None
    return best_accident


def _match_detections_to_accidents(
    db: Session,
    new_detections: List[Detection],
    matching_accidents: List[Accident],
    now: datetime,
) -> tuple[list[int], list[int], set[int]]:
    new_accidents: list[int] = []
    updated_accidents: list[int] = []
    matched_accident_ids: set[int] = set()

    for detection in new_detections:
        bbox_det = _bbox_from_detection(detection)
        matching_accident = _find_best_matching_accident(bbox_det, matching_accidents)

        if matching_accident:
            matching_accident.last_seen = now
            matching_accident.confidence = max(
                matching_accident.confidence or 0, detection.confidence
            )
            matching_accident.status_updated_at = now
            matching_accident.missed_screenshots = 0
            matching_accident.event_status = "updated"
            detection.accident_id = matching_accident.id
            matched_accident_ids.add(matching_accident.id)
            updated_accidents.append(matching_accident.id)
        else:
            new_accident = Accident(
                bbox_x1=detection.bbox_x1,
                bbox_y1=detection.bbox_y1,
                bbox_x2=detection.bbox_x2,
                bbox_y2=detection.bbox_y2,
                confidence=detection.confidence,
                first_seen=now,
                last_seen=now,
                event_status="new",
                is_active=True,
                missed_screenshots=0,
                status_updated_at=now,
            )
            db.add(new_accident)
            db.flush()
            detection.accident_id = new_accident.id
            new_accidents.append(new_accident.id)

    return new_accidents, updated_accidents, matched_accident_ids


# фильтр для закрытия ДТП: пропущенные кадры -> resolved
def _resolve_unmatched_accidents(
    db: Session,
    all_active_accidents: List[Accident],
    matched_accident_ids: set[int],
    now: datetime,
) -> list[int]:
    resolved_accidents: list[int] = []
    for accident in all_active_accidents:
        if accident.id in matched_accident_ids:
            continue
        accident.missed_screenshots += 1
        accident.status_updated_at = now
        if accident.missed_screenshots >= MISSED_FRAMES_TO_RESOLVE:
            accident.event_status = "resolved"
            accident.is_active = False
            accident.resolved_at = now
            delete_notifications_for_accident(db, accident.id)
            resolved_accidents.append(accident.id)
    return resolved_accidents


def process_screenshot_detections(db: Session, detections: List[Dict]) -> Dict[str, List[int]]:
    now = datetime.now(timezone.utc)
    new_detections = _save_detections(db, detections)

    cutoff = now - timedelta(hours=ACTIVE_WINDOW_HOURS)
    matching_accidents = (
        db.query(Accident)
        .filter(Accident.is_active.is_(True))
        .filter(Accident.last_seen >= cutoff)
        .all()
    )
    all_active_accidents = db.query(Accident).filter(Accident.is_active.is_(True)).all()

    new_accidents, updated_accidents, matched_ids = _match_detections_to_accidents(
        db, new_detections, matching_accidents, now
    )
    resolved_accidents = _resolve_unmatched_accidents(
        db, all_active_accidents, matched_ids, now
    )

    return {
        "new_accidents": list(dict.fromkeys(new_accidents)),
        "updated_accidents": list(dict.fromkeys(updated_accidents)),
        "resolved_accidents": list(dict.fromkeys(resolved_accidents)),
    }
