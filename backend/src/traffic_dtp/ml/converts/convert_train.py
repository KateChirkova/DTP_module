# VOC XML train -> YOLO .txt (размеры кадра из PNG/JPG)
import glob
import os

import matplotlib.pyplot as plt

from src.traffic_dtp.ml.converts.voc_to_yolo import write_yolo_labels_from_xml


def convert_xml_to_yolo(xml_path, img_path, output_path):
    img = plt.imread(img_path)
    img_height, img_width = img.shape[:2]
    write_yolo_labels_from_xml(xml_path, output_path, img_width, img_height)


xml_files = glob.glob("dataset/labels/train/*.xml")
print(f"Найдено {len(xml_files)} XML файлов")

for i, xml_file in enumerate(xml_files):
    basename = os.path.splitext(os.path.basename(xml_file))[0]

    img_patterns = [
        f"dataset/images/train/**/{basename}.png",
        f"dataset/images/train/**/{basename}.jpg",
    ]

    img_path = None
    for pattern in img_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            img_path = matches[0]
            break

    if img_path:
        txt_path = f"dataset/labels/train/{basename}.txt"
        convert_xml_to_yolo(xml_file, img_path, txt_path)
        print(f"{i + 1}/{len(xml_files)} {basename}")
    else:
        print(f"PNG не найден для {basename}")

print("Конвертация завершена")
