import pytest
from geohash_manager.main import GeohashManager


@pytest.fixture(scope="session")
def manager():
    return GeohashManager()


## information


@pytest.mark.parametrize("x,y,r,expected", [(127.031767, 37, 20000, 63)])
def test_xyr_to_rects(manager, x, y, r, expected):
    ret = manager.xyr_to_rects(x=x, y=y, r=r)
    assert len(ret) == expected
