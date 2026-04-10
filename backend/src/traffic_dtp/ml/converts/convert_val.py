# convert.py
import os
import xml.etree.ElementTree as ET
from PIL import Image


def xml_to_yolo(xml_path, txt_path, img_width, img_height):
    # Конвертируем один файл xml в txt
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with open(txt_path, 'w') as f:
        for obj in root.findall('object'):
            # Координаты из XML
            xmin = float(obj.find('bndbox/xmin').text)
            ymin = float(obj.find('bndbox/ymin').text)
            xmax = float(obj.find('bndbox/xmax').text)
            ymax = float(obj.find('bndbox/ymax').text)

            # Конвертация в YOLO формат
            x_center = (xmin + xmax) / 2 / img_width
            y_center = (ymin + ymax) / 2 / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            # Запись: class_id x_center y_center width height
            f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


def convert_folder(xml_folder, img_folder, output_folder):
    # Конвертируем всю папку xml в txt
    os.makedirs(output_folder, exist_ok=True)

    for xml_file in os.listdir(xml_folder):
        if xml_file.endswith('.xml'):
            # Путь к файлу
            xml_path = os.path.join(xml_folder, xml_file)
            base_name = os.path.splitext(xml_file)[0]

            # Найти соответствующую картинку
            img_path = None
            for ext in ['.jpg', '.jpeg', '.png']:
                test_path = os.path.join(img_folder, base_name + ext)
                if os.path.exists(test_path):
                    img_path = test_path
                    break

            if img_path:
                # Получить размер картинки
                with Image.open(img_path) as img:
                    width, height = img.size

                # Конвертировать
                txt_path = os.path.join(output_folder, base_name + '.txt')
                xml_to_yolo(xml_path, txt_path, width, height)
                print(f"✓ {base_name}.xml → {base_name}.txt")
            else:
                print(f"✗ Картинка не найдена: {base_name}")


if __name__ == "__main__":
    xml_folder = "dataset/labels/val_xml"
    img_folder = "dataset/images/val"
    output_folder = "dataset/labels/val"

    convert_folder(xml_folder, img_folder, output_folder)
    print("Конвертация завершена!")