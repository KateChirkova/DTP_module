# внутренний ключ watchdog -> POST /detections
from __future__ import annotations

import logging
import os

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)

ENV_KEY = "DTP_INTERNAL_API_KEY"
HEADER_NAME = "X-Internal-Key"


def configured_internal_key() -> str | None:
    key = (os.getenv(ENV_KEY) or "").strip()
    return key or None


def verify_internal_api_key(
    x_internal_key: str | None = Header(default=None, alias=HEADER_NAME),
) -> None:
    expected = configured_internal_key()
    if not expected:
        return
    if not x_internal_key or x_internal_key != expected:
        logger.warning("Internal API key rejected for POST /detections")
        raise HTTPException(
            status_code=403,
            detail="Недопустимый или отсутствующий внутренний ключ API",
        )
