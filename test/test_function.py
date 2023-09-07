import pytest
from geohash_manager import RectShape, GeohashManager


@pytest.fixture(scope="session")
def manager():
    return GeohashManager()


## information


@pytest.mark.parametrize("x,y,r,expected", [(127.031767, 37, 20000, 140)])
def test_xyr_to_rects(manager: GeohashManager, x, y, r, expected):
    ret = manager.xyr_to_rects(x=x, y=y, r=r)
    ##duplicated_check
    result = [manager.rect_geohash(i) for i in ret]
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


def test_rect_to_geohash(manager: GeohashManager):
    rect = RectShape(
        xmin=127.6171875,
        ymin=34.62890625,
        xmax=127.96875,
        ymax=34.8046875,
    )
    ret = manager.rect_geohash(rect=rect)
    assert ret is not None, f"error case : {ret}"


@pytest.mark.parametrize("geohash", ["wydbb"])
def test_rect_geohash(manager, geohash):
    ret = manager.geohash_rect(geohash)
    ret_geohash = manager.rect_geohash(ret)
    assert ret_geohash == geohash
    error_case = RectShape(
        xmax=127.96875, xmin=127.9248046875, ymax=34.8046875, ymin=34.7607421875
    )
    ret = manager.rect_geohash(error_case)
    assert ret is not None, f"error case : {ret}"
    error_case_1 = RectShape(
        xmax=127.96875, xmin=127.6171875, ymax=34.8046875, ymin=34.62890625
    )
    y = error_case_1.ymax - error_case_1.ymin
    x = error_case_1.xmax - error_case_1.xmin
    print(x, y)
    ret = manager.rect_geohash(error_case_1)
    assert ret is not None, f"error case : {ret}"
    error_case_2 = RectShape(
        xmax=127.75039672851562,
        xmin=127.75005340576172,
        ymax=34.737396240234375,
        ymin=34.73722457885742,
    )
    ret = manager.rect_geohash(error_case_2)
    assert ret is not None, f"error case : {ret}"  ## fixed, extend geohash_length 7->8
    error_case_3 = RectShape(
        xmin=127.9248046875,
        ymin=34.7607421875,
        xmax=127.96875,
        ymax=34.8046875,
    )
    ret = manager.rect_geohash(error_case_3)
    assert ret is not None, f"error case : {ret}"  ## fixed, extend geohash_length 7->8


def test_gen_geohash():
    import pygeohash as pgh

    ret = pgh.decode_exactly("wydbbxxx")
    print(ret[2] * 2, ret[3] * 2)


def test_position_geohashObject(manager: GeohashManager):
    position = (127.056146, 37.505308)
    precision = 6
    position, geohash_obj, bias = manager.position_geohashobj(
        position=position, precision=precision
    )
    assert geohash_obj.geohash == "wydm75"
    assert bias == "bottomleft"


def test_position_neighbor(manager: GeohashManager):
    curent_position = (127.96875, 34.8046875)
    precision = 6
    geohash_obj = manager.neighbor(position=curent_position, precision=precision)
    assert len(geohash_obj.geohash) == 6, f"neighbor_geohash : {geohash_obj.geohash}"
    assert len(geohash_obj.bbox) == 4, f"bbox : {geohash_obj.bbox}"


@pytest.mark.parametrize(
    "input_param,output_param",
    [({"position": (127.96875, 34.8046875)}, True), ({"geohash": "wydbb"}, True)],
)
def test_position_neighbors(manager: GeohashManager, input_param, output_param):
    if "position" in input_param.keys():
        curent_position = input_param["position"]
        precision = 6
        ## neighbors : input position or geohash, precision nullable direction
        geohashes = manager.neighbors(position=curent_position, precision=precision)
        assert (
            len(geohashes.geohashes) == 8
        ), f"neighbor_geohash : {geohashes.geohashes}"
        assert len(geohashes.order) == 8, f"order : {geohashes.order}"
        assert type(geohashes.outer_rect) == RectShape, "outer type check"
    elif "geohash" in input_param.keys():
        geohash = input_param["geohash"]
        precision = 6
        geohashes = manager.neighbors(geohash=geohash, precision=precision)
        ## precision ignore, geohash length overrided
        assert len(geohashes.geohashes[0].geohash) == len(
            input_param["geohash"]
        ), f"geohash : {geohashes}"

    else:
        raise ValueError("input_param must be current_position or geohash")
