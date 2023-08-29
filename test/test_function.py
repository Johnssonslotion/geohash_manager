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
        xmin=127.6171875,
        ymin=34.62890625,
        xmax=127.96875,
        ymax=34.8046875,
    )
    ret, geo_set = manager.rect_to_rects(bbox=rect.items)
    print("temp")


def test_rect_to_geohash(manager):
    rect = RectShape(
        xmin=127.6171875,
        ymin=34.62890625,
        xmax=127.96875,
        ymax=34.8046875,
    )
    ret = manager.rect_to_geohash(bbox=rect.items)

    print("temp")


@pytest.mark.parametrize("geohash", ["wydbb"])
def test_rect_geohash(manager, geohash):
    ret = manager.geohash_rect(geohash)
    ret_geohash = manager.rect_geohash(ret)
    assert ret_geohash == geohash
    error_case = RectShape(
        xmax=127.96875, xmin=127.9248046875, ymax=34.8046875, ymin=34.7607421875
    )
    ret = manager.rect_geohash(error_case)
    assert ret is not None, "error case"
