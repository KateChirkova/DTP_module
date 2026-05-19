# тесты сопоставления детекций и закрытия ДТП
from src.traffic_dtp.services.accident_processor import process_screenshot_detections
from src.traffic_dtp.db.models import Accident


# новая детекция без совпадения IoU -> новый accident
def test_create_new_accident(db_session):
    result = process_screenshot_detections(
        db_session,
        [
            {
                "confidence": 0.92,
                "bbox_x1": 10,
                "bbox_y1": 20,
                "bbox_x2": 100,
                "bbox_y2": 120,
            }
        ],
    )

    assert len(result["new_accidents"]) == 1
    accident = db_session.query(Accident).first()
    assert accident is not None
    assert accident.event_status == "new"
    assert accident.is_active is True


# пересекающийся bbox -> update, сброс missed_screenshots
def test_update_existing_accident(db_session):
    process_screenshot_detections(
        db_session,
        [
            {
                "confidence": 0.90,
                "bbox_x1": 10,
                "bbox_y1": 20,
                "bbox_x2": 100,
                "bbox_y2": 120,
            }
        ],
    )

    accident = db_session.query(Accident).first()
    assert accident is not None

    second = process_screenshot_detections(
        db_session,
        [
            {
                "confidence": 0.95,
                "bbox_x1": 12,
                "bbox_y1": 22,
                "bbox_x2": 102,
                "bbox_y2": 122,
            }
        ],
    )

    assert len(second["updated_accidents"]) == 1
    accident = db_session.query(Accident).first()
    assert accident.missed_screenshots == 0


# два кадра без детекции в bbox -> resolved
def test_accident_resolved_after_two_frames_without_detection(db_session):
    process_screenshot_detections(
        db_session,
        [
            {
                "confidence": 0.9,
                "bbox_x1": 10,
                "bbox_y1": 10,
                "bbox_x2": 50,
                "bbox_y2": 50,
            }
        ],
    )
    db_session.flush()
    acc_id = db_session.query(Accident).first().id
    assert db_session.get(Accident, acc_id).is_active is True

    process_screenshot_detections(db_session, [])
    db_session.flush()
    assert db_session.get(Accident, acc_id).missed_screenshots == 1
    assert db_session.get(Accident, acc_id).is_active is True

    process_screenshot_detections(db_session, [])
    db_session.flush()
    final = db_session.get(Accident, acc_id)
    assert final.is_active is False
    assert final.event_status == "resolved"
