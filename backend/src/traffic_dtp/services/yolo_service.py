import subprocess
import json
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).parent.parent  # src/traffic_dtp/

ML_VENV_PYTHON = BASE_DIR / "ml/venv_ml/Scripts/python.exe"
YOLO_SCRIPT = BASE_DIR / "services/yolo_predict.py"


def predict_accident(image_path: str) -> Dict:
    # services/venv_api -> ml/venv_ml
    cmd = [
        str(ML_VENV_PYTHON),
        str(YOLO_SCRIPT),
        image_path
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=30, cwd=str(BASE_DIR)
    )

    if result.returncode == 0:
        return json.loads(result.stdout.strip())

    # Fallback при ошибке ML
    return {
        "confidence": 0.0,
        "bbox": [],
        "screenshotid": int(time.time())
    }