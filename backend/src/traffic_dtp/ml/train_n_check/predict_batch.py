from ultralytics import YOLO
from pathlib import Path

model = YOLO("backend/src/traffic_dtp/ml/runs/detect/dtp_krasnodar_light9/weights/best.pt")

images_dir = Path("/ml/dataset/for_predict")
out_dir = Path("/ml/dataset/predictions")
out_dir.mkdir(parents=True, exist_ok=True)

for img_path in images_dir.glob("*.png"):
    results = model(img_path)
    results[0].save(filename=str(out_dir / img_path.name))