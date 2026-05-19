import pytest

# тесты calculate_iou
from src.traffic_dtp.services.accident_processor import calculate_iou


@pytest.mark.parametrize(
    "box_a,box_b,expected",
    [
        ([0, 0, 10, 10], [0, 0, 10, 10], 1.0),
        ([0, 0, 10, 10], [10, 0, 20, 10], 0.0),
        ([0, 0, 10, 10], [5, 0, 15, 10], 1.0 / 3.0),
    ],
)
def test_calculate_iou_known_pairs(box_a, box_b, expected):
    got = calculate_iou(box_a, box_b)
    assert abs(got - expected) < 1e-6


def test_calculate_iou_no_overlap():
    assert calculate_iou([0, 0, 5, 5], [10, 10, 15, 15]) == 0.0


def test_calculate_iou_zero_area_union():
    # вырожденные боксы: union 0
    assert calculate_iou([0, 0, 0, 10], [0, 0, 0, 10]) == 0.0
