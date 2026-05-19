import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.traffic_dtp.db.session import get_db

logger = logging.getLogger(__name__)
from src.traffic_dtp.services.detection_pipeline import process_screenshot_file
from src.traffic_dtp.services.internal_auth import verify_internal_api_key
from src.traffic_dtp.services.paths import resolve_screenshot_path

router = APIRouter(prefix="/api/v1", tags=["detections"])


class ScreenshotPath(BaseModel):
    screenshot_path: str


# внутренний эндпоинт: watchdog отдаёт имя файла скриншота
@router.post("/detections")
async def process_screenshot(
    request: ScreenshotPath,
    _internal: None = Depends(verify_internal_api_key),
    db: Session = Depends(get_db),
):
    filename, full_path = resolve_screenshot_path(request.screenshot_path)

    if not full_path.exists():
        logger.warning(
            "Screenshot not found: filename=%s path=%s",
            filename,
            full_path,
        )
        raise HTTPException(
            status_code=404,
            detail=f"Скриншот «{filename}» не найден: {full_path}",
        )

    try:
        return await process_screenshot_file(db, full_path, filename)
    except FileNotFoundError as e:
        logger.warning("Screenshot unavailable: %s", e)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception:
        logger.exception(
            "Detection pipeline failed: filename=%s path=%s",
            filename,
            full_path,
        )
        raise
