from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset/data.yaml",
    epochs=30,
    imgsz=1280,
    batch=4,
    name="dtp_krasnodar_light",
)

print("Обучение завершено. Веса сохранены в runs/detect/dtp_krasnodar_light/weights/best.pt")