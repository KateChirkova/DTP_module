# VOC bbox -> YOLO normalized
from __future__ import annotations

import xml.etree.ElementTree as ET


def voc_box_to_yolo(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    img_width: float,
    img_height: float,
) -> tuple[float, float, float, float]:
    x_center = ((xmin + xmax) / 2) / img_width
    y_center = ((ymin + ymax) / 2) / img_height
    width = (xmax - xmin) / img_width
    height = (ymax - ymin) / img_height
    return x_center, y_center, width, height


# разбор Pascal VOC XML -> строки class xc yc w h
def write_yolo_labels_from_xml(
    xml_path: str,
    output_path: str,
    img_width: float,
    img_height: float,
    *,
    class_id: int = 0,
) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    objects = root.findall("object")

    with open(output_path, "w", encoding="utf-8") as f:
        for obj in objects:
            bndbox = obj.find("bndbox")
            if bndbox is None:
                continue
            xmin = float(bndbox.find("xmin").text)
            ymin = float(bndbox.find("ymin").text)
            xmax = float(bndbox.find("xmax").text)
            ymax = float(bndbox.find("ymax").text)
            xc, yc, w, h = voc_box_to_yolo(xmin, ymin, xmax, ymax, img_width, img_height)
            f.write(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
