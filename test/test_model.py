import random
import pytest
from geohash_manager.model import CircleShape, RectShape


## #TODO pytest로 테스트 코드?
def test_spatial_model():
    ## x == lng, y == lat (GEOJSON order) x축 경도, y축 위도 x(범위 : -180 ~ 180), y(범위 : -90 ~ 90)
    center_1 = (random.uniform(-180, 180), random.uniform(-90, 90))  ## swap
    center_rev = (
        random.uniform(-90, 90),
        random.uniform(90, 180),
    )  ## 정상동작
    rect_1 = (
        random.uniform(90, 180),
        random.uniform(-90, 90),
        random.uniform(90, 180),
        random.uniform(-90, 90),
    )
    rect_2 = (
        random.uniform(-90, 90),
        random.uniform(90, 180),
        random.uniform(-90, 90),
        random.uniform(90, 180),
    )

    case_1 = CircleShape(x=center_1[0], y=center_1[1], radius=2000)
    assert (
        case_1.x == center_1[0] and case_1.y == center_1[1] and case_1.radius == 2000
    ), f"case_1, normally input(sep) : {case_1}"
    case_2 = CircleShape(center=center_1, radius=20000)
    assert (
        case_2.x == center_1[0] and case_2.y == center_1[1] and case_2.radius == 20000
    ), f"case_2, normally input(tuple): {case_2}"
    case_3 = CircleShape(center=center_rev, radius=20000)
    assert (
        case_3.x == center_rev[1]
        and case_3.y == center_rev[0]
        and case_3.radius == 20000
    ), f"case_3 : {case_3}"
    case_4 = RectShape(xmin=rect_1[0], ymin=rect_1[1], xmax=rect_1[2], ymax=rect_1[3])
    print(f"\n, rect_4 : {case_4}")
    assert (
        case_4.xmin == rect_1[0]
        and case_4.ymin == rect_1[1]
        and case_4.xmax == rect_1[2]
        and case_4.ymax == rect_1[3]
    ), "rect_1"
    case_5 = RectShape(xmin=rect_2[0], ymin=rect_2[1], xmax=rect_2[2], ymax=rect_2[3])
    assert (
        case_5.xmin == rect_2[1]
        and case_5.ymin == rect_2[0]
        and case_5.xmax == rect_2[3]
        and case_5.ymax == rect_2[2]
    ), "rect_2"

    case_6 = RectShape(bbox=rect_1)
    assert (
        case_6.xmin == rect_1[0]
        and case_6.ymin == rect_1[1]
        and case_6.xmax == rect_1[2]
        and case_6.ymax == rect_1[3]
    ), "rect_1"

    case_7 = RectShape(bbox=rect_2)
    assert (
        case_7.xmin == rect_2[1]
        and case_7.ymin == rect_2[0]
        and case_7.xmax == rect_2[3]
        and case_7.ymax == rect_2[2]
    ), "rect_2"
