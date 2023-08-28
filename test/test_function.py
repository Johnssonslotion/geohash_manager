import pytest
from geohash_manager import RectShape, GeohashManager


@pytest.fixture(scope="session")
def manager():
    return GeohashManager()


## information


@pytest.mark.parametrize("x,y,r,expected", [(127.031767, 37, 20000, 63)])
def test_xyr_to_rects(manager, x, y, r, expected):
    ret = manager.xyr_to_rects(x=x, y=y, r=r)
    assert len(ret) == expected


def test_rect_to_rects(manager):
    rect = RectShape(
        xmin=127.031767,
        ymin=37.497175,
        xmax=127.031767,
        ymax=37.497175,
    )
    ret = manager.rect_to_rects(bbox=rect.items)
