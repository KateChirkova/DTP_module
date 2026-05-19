# YOLO: HTTP worker (Docker) или in-process (локально)
import json
import logging
import os
import urllib.error
import urllib.request
from typing import Dict

from src.traffic_dtp.services.paths import resolve_project_path

logger = logging.getLogger(__name__)


def _predict_inprocess(image_path: str) -> Dict:
    from src.traffic_dtp.services.yolo_predict import predict_accident as run_predict

    full_image = resolve_project_path(image_path)
    logger.info("YOLO in-process: %s", full_image)
    out = run_predict(str(full_image))
    return out if isinstance(out, dict) else {"detections": []}


def _predict_via_worker(base_url: str, image_path: str) -> Dict:
    url = base_url.rstrip("/") + "/predict"
    resolved = str(resolve_project_path(image_path))
    payload = json.dumps({"path": resolved}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def warmup_yolo_model() -> None:
    worker = os.getenv("YOLO_WORKER_URL", "").strip()
    if worker:
        return
    from src.traffic_dtp.services.yolo_predict import get_model

    get_model()
    logger.info("YOLO model preloaded (in-process)")


def predict_accident(image_path: str) -> Dict:
    worker = os.getenv("YOLO_WORKER_URL", "").strip()
    if worker:
        try:
            return _predict_via_worker(worker, image_path)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
            logger.warning("YOLO worker (%s) недоступен: %s — in-process fallback", worker, e)

    return _predict_inprocess(image_path)
