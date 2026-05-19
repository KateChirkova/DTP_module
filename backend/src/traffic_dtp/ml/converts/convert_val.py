# VOC XML val -> YOLO .txt
import os

from PIL import Image

from src.traffic_dtp.ml.converts.voc_to_yolo import write_yolo_labels_from_xml


def convert_folder(xml_folder, img_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for xml_file in os.listdir(xml_folder):
        if not xml_file.endswith(".xml"):
            continue
        xml_path = os.path.join(xml_folder, xml_file)
        base_name = os.path.splitext(xml_file)[0]

        img_path = None
        for ext in [".jpg", ".jpeg", ".png"]:
            test_path = os.path.join(img_folder, base_name + ext)
            if os.path.exists(test_path):
                img_path = test_path
                break

        if img_path:
            with Image.open(img_path) as img:
                width, height = img.size
            txt_path = os.path.join(output_folder, base_name + ".txt")
            write_yolo_labels_from_xml(xml_path, txt_path, width, height)
            print(f"{base_name}.xml -> {base_name}.txt")
        else:
            print(f"Картинка не найдена: {base_name}")


if __name__ == "__main__":
    convert_folder(
        "dataset/labels/val_xml",
        "dataset/images/val",
        "dataset/labels/val",
    )
    print("Конвертация завершена!")
