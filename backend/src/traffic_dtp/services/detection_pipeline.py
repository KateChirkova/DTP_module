# цепочка: скриншот -> YOLO -> accidents -> уведомления -> WebSocket
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from src.traffic_dtp.db.models import Accident
from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.services.accident_processor import process_screenshot_detections
from src.traffic_dtp.services.notifications import (
    create_notification,
    push_unread_counts_all_users,
)
from src.traffic_dtp.services.ws_manager import manager

logger = logging.getLogger(__name__)

_EVENT_BY_BUCKET = (
    ("new_accidents", "newaccident"),
    ("updated_accidents", "accidentupdated"),
    ("resolved_accidents", "accidentresolved"),
)


def _accident_event_payload(accident: Accident) -> dict[str, Any]:
    return {
        "id": accident.id,
        "status": accident.event_status,
        "created_at": accident.first_seen.isoformat() if accident.first_seen else None,
    }


# счётчики в UI — отдельная сессия, не блокирует WS
async def _push_unread_counts_background() -> None:
    db = SessionLocal()
    try:
        await push_unread_counts_all_users(db, manager)
    except Exception:
        logger.exception("push_unread_counts failed")
    finally:
        db.close()


async def _emit_accident_event(
    *,
    accident_id: int,
    bucket: str,
    event_name: str,
    by_id: dict[int, Accident],
) -> bool:
    accident = by_id.get(accident_id)
    if not accident:
        logger.error(
            "Accident missing for WS broadcast: bucket=%s event=%s accident_id=%s",
            bucket,
            event_name,
            accident_id,
        )
        return False
    await manager.broadcast_to_all({
        "event": event_name,
        "data": _accident_event_payload(accident),
    })
    return True


async def _broadcast_accident_changes(db: Session, result: dict[str, list[int]]) -> None:
    new_ids = result.get("new_accidents", [])
    if not new_ids and not any(result.get(key) for key, _ in _EVENT_BY_BUCKET):
        return

    all_ids: set[int] = set()
    for key, _ in _EVENT_BY_BUCKET:
        all_ids.update(result.get(key, []))
    if not all_ids:
        return

    accidents = db.query(Accident).filter(Accident.id.in_(all_ids)).all()
    by_id = {acc.id: acc for acc in accidents}

    if len(by_id) < len(all_ids):
        missing = sorted(all_ids - by_id.keys())
        logger.error(
            "Accident rows missing after commit: ids=%s (pipeline result=%s)",
            missing,
            {k: result.get(k, []) for k, _ in _EVENT_BY_BUCKET},
        )

    for accident_id in new_ids:
        await _emit_accident_event(
            accident_id=accident_id,
            bucket="new_accidents",
            event_name="newaccident",
            by_id=by_id,
        )

    for bucket_key, event_name in _EVENT_BY_BUCKET:
        if bucket_key == "new_accidents":
            continue
        for accident_id in result.get(bucket_key, []):
            await _emit_accident_event(
                accident_id=accident_id,
                bucket=bucket_key,
                event_name=event_name,
                by_id=by_id,
            )

    if new_ids:
        asyncio.create_task(_push_unread_counts_background())


async def process_screenshot_file(
    db: Session,
    full_path: Path,
    filename: str,
) -> dict[str, Any]:
    try:
        file_size = full_path.stat().st_size
    except OSError as e:
        logger.error("Screenshot stat failed: filename=%s path=%s", filename, full_path)
        raise FileNotFoundError(f"Скриншот недоступен: {filename} ({e})") from e

    if file_size == 0:
        detections: list[dict] = []
    else:
        try:
            from src.traffic_dtp.services.yolo_service import predict_accident as run_yolo

            raw = await asyncio.to_thread(run_yolo, str(full_path))
            detections = raw.get("detections", [])
        except Exception as e:
            logger.warning("YOLO failed for %s: %s", filename, e, exc_info=True)
            detections = []

    try:
        result = process_screenshot_detections(db, detections)
    except Exception:
        logger.exception(
            "process_screenshot_detections failed: filename=%s detections=%s",
            filename,
            len(detections),
        )
        raise

    for acc_id in result.get("new_accidents", []):
        notification = create_notification(db, acc_id)
        if notification is None:
            logger.error(
                "Notification not created for new accident: accident_id=%s filename=%s",
                acc_id,
                filename,
            )

    try:
        db.commit()
    except Exception:
        logger.exception(
            "Detection pipeline commit failed: filename=%s result=%s",
            filename,
            result,
        )
        raise

    await _broadcast_accident_changes(db, result)

    response: dict[str, Any] = {
        "success": True,
        "filename": filename,
        "detections_found": len(detections),
        "new_accidents": len(result.get("new_accidents", [])),
        "updated_accidents": len(result.get("updated_accidents", [])),
        "resolved_accidents": len(result.get("resolved_accidents", [])),
    }
    if not detections:
        response["message"] = "YOLO не нашёл ДТП"
    return response
