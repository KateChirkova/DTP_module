from src.traffic_dtp.services.accident_processor import process_screenshot_detections
from src.traffic_dtp.db.models import Accident

def test_create_new_accident(db_session):
    result = process_screenshot_detections(
        db_session,
        [{
            "confidence": 0.92,
            "bbox_x1": 10,
            "bbox_y1": 20,
            "bbox_x2": 100,
            "bbox_y2": 120,
        }]
    )

    assert len(result["new_accidents"]) == 1
    accident = db_session.query(Accident).first()
    assert accident is not None
    assert accident.status == "active"
    assert accident.is_active is True

def test_update_existing_accident(db_session):
    first = process_screenshot_detections(
        db_session,
        [{
            "confidence": 0.90,
            "bbox_x1": 10,
            "bbox_y1": 20,
            "bbox_x2": 100,
            "bbox_y2": 120,
        }]
    )

    accident = db_session.query(Accident).first()
    assert accident is not None

    second = process_screenshot_detections(
        db_session,
        [{
            "confidence": 0.95,
            "bbox_x1": 12,
            "bbox_y1": 22,
            "bbox_x2": 102,
            "bbox_y2": 122,
        }]
    )

    assert len(second["updated_accidents"]) == 1
    accident = db_session.query(Accident).first()
    assert accident.missed_screenshots == 0