import os
import glob
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt  # ← ДОБАВЛЕНО!


def convert_xml_to_yolo(xml_path, img_path, output_path):
    # Размер изображения
    img = plt.imread(img_path)
    img_height, img_width = img.shape[:2]

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Если объектов нет — пустой TXT
    objects = root.findall('object')
    if not objects:
        open(output_path, 'w').close()
        return

    with open(output_path, 'w') as f:
        for obj in objects:
            class_name = obj.find('name').text
            class_id = 0  # dtp = класс 0

            bndbox = obj.find('bndbox')
            xmin = float(bndbox.find('xmin').text)
            ymin = float(bndbox.find('ymin').text)
            xmax = float(bndbox.find('xmax').text)
            ymax = float(bndbox.find('ymax').text)

            # Нормализация YOLO
            x_center = ((xmin + xmax) / 2) / img_width
            y_center = ((ymin + ymax) / 2) / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


# Конвертация
xml_files = glob.glob("dataset/labels/train/*.xml")
print(f"Найдено {len(xml_files)} XML файлов")

for i, xml_file in enumerate(xml_files):
    basename = os.path.splitext(os.path.basename(xml_file))[0]

    # Найти PNG в images/train
    img_patterns = [
        f"dataset/images/train/**/{basename}.png",
        f"dataset/images/train/**/{basename}.jpg"
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
        print(f"✓ {i + 1}/{len(xml_files)} {basename}")
    else:
        print(f"PNG не найден для {basename}")

print("Конвертация завершена")