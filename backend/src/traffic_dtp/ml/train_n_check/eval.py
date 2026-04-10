from ultralytics import YOLO

model = YOLO("backend/src/traffic_dtp/ml/runs/detect/dtp_krasnodar_light9/weights/best.pt")

metrics = model.val(
    data="ml/dataset/data.yaml",
    split="val"
)

print("mAP@0.5:0.95:", metrics.box.map)
print("mAP@0.5:", metrics.box.map50)
print("precision (mp):", metrics.box.mp)
print("recall (mr):", metrics.box.mr)