# backend/src/traffic_dtp/ml/train.py
"""
Скрипт воспроизведения обучения YOLOv8 модели для детекции ДТП.
Обучено через терминал.
"""

from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # базовая модель

results = model.train(
    data="dataset/data.yaml",     # Датасет Краснодар
    epochs=30,                    # эпохи
    imgsz=1280,                   # размер изображения
    batch=4,                      # размер батча
    name="dtp_krasnodar_light",    # имя папки runs/detect/accident_detection/
)

print("Обучение завершено. Веса сохранены в runs/detect/dtp_krasnodar_light/weights/best.pt")