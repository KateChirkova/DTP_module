import subprocess
import json
import time
from pathlib import Path
from typing import Dict

# services/ -> traffic_dtp/ -> src/ -> backend/ -> D:\DTP_Akaito
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
print(f"BASE_DIR: {BASE_DIR}")  # Должен быть D:\DTP_Akaito

ML_VENV_PYTHON = BASE_DIR / "backend" / "src" / "traffic_dtp" / "ml" / "venv-ml" / "Scripts" / "python.exe"
YOLO_SCRIPT = BASE_DIR / "backend" / "src" / "traffic_dtp" / "services" / "yolo_predict.py"

print(f"ML: {ML_VENV_PYTHON.exists()}")
print(f"Script: {YOLO_SCRIPT.exists()}")


def predict_accident(image_path: str) -> Dict:
    full_image = BASE_DIR / image_path  # Относительно корня
    cmd = [str(ML_VENV_PYTHON), str(YOLO_SCRIPT), str(full_image)]

    print(f"🚀 CMD: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(BASE_DIR))

    print(f"STDOUT: {result.stdout[:200]}...")
    print(f"STDERR: {result.stderr[:200]}...")
    print(f"Return code: {result.returncode}")

    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout.strip())

    return {"detections": []}