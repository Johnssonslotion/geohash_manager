import pytest
from geohash_manager import RectShape, GeohashManager
from geohash_manager.model.shape_model import GeohashObject
import time
import pygeohash as pgh

# @pytest.fixture(scope="session")
# def manager():
#     return GeohashManager()


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
    assert geohash_obj.geohash_str == "wydm75"
    assert bias == "bottomleft"


def test_position_neighbor(manager: GeohashManager):
    curent_position = (127.96875, 34.8046875)
    precision = 6
    geohash_obj = manager.neighbor(position=curent_position, precision=precision)
    assert (
        len(geohash_obj.geohash_str) == 6
    ), f"neighbor_geohash : {geohash_obj.geohash}"
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
        position, geohash_obj, bias = manager.position_geohashobj(
            position=curent_position, precision=precision
        )
        geohashes = manager.neighbors(position=curent_position, precision=precision)

        assert (
            len(geohashes.neighbers) == 8
        ), f"neighbor_geohash : {geohashes.neighbers}"
        assert len(geohashes.order) == 8, f"order : {geohashes.order}"
        assert (
            geohashes.geohash.geohash_str == geohash_obj.geohash_str
        ), f"geohash : {geohashes.geohash}"
        # geohash_string_trim = geohash_obj.geohash_str[: precision - 1]
        # for i in geohashes.neighbers:
        #     assert type(i) == GeohashObject, "neighbers type check"
        #     assert (
        #         i.geohash_str[: precision - 1] == geohash_string_trim
        #     ), "geohash trim check"
        assert type(geohashes.outer_rect) == RectShape, "outer type check"
    elif "geohash" in input_param.keys():
        geohash = input_param["geohash"]
        precision = 6
        geohash_string_trim = geohash[: len(geohash) - 1]
        geohashes = manager.neighbors(geohash=geohash, precision=precision)
        ## precision ignore, geohash length overrided
        assert (
            geohashes.geohash.geohash_str == geohash
        ), f"geohash : {geohashes.geohash}"
        assert len(geohashes.neighbers[0].geohash_str) == len(
            input_param["geohash"]
        ), f"geohash : {geohashes}"
        # for i in geohashes.neighbers:
        #     assert type(i) == GeohashObject, "neighbers type check"
        #     assert (
        #         i.geohash_str[: precision - 1] == geohash_string_trim
        #     ), "geohash trim check"
        assert type(geohashes.outer_rect) == RectShape, "outer type check"

    else:
        raise ValueError("input_param must be current_position or geohash")


def test_search_neighborhood(util_latlng):
    target = util_latlng
    prec = 6
    ## time check
    start_time = time.time()
    manager = GeohashManager()
    geohash_neighbor = manager.neighbor(
        position=(target["lng"], target["lat"]), precision=prec
    )
    # geohash, bbox, _ =latlng_rect(target["lat"], target["lng"],precision=prec)
    hashing_time = time.time() - start_time
    print(
        f"\nhashing time: {hashing_time:4f}s",
    )

    assert geohash_neighbor.geohash_str is not None
    assert geohash_neighbor.bbox is not None
    ret = manager.neighbors(
        geohash=geohash_neighbor.geohash_str, precision=prec, direction="all"
    )

    searching_time = time.time() - start_time
    print(f"searching time: {searching_time:4f}s")
    ## size_check & length_check
    assert len(ret.neighbers) == 8

    ## edge check
    bbox = ret.geohash.bbox  ## center area bbox
    single_top = manager.geohash_rect(ret.neighbers[0].geohash_str)
    single_bottom = manager.geohash_rect(ret.neighbers[4].geohash_str)
    single_left = manager.geohash_rect(ret.neighbers[6].geohash_str)
    single_right = manager.geohash_rect(ret.neighbers[2].geohash_str)
    single_top_left = manager.geohash_rect(ret.neighbers[-1].geohash_str)
    single_top_right = manager.geohash_rect(ret.neighbers[1].geohash_str)
    single_bottom_left = manager.geohash_rect(ret.neighbers[5].geohash_str)
    single_bottom_right = manager.geohash_rect(ret.neighbers[3].geohash_str)

    center_topright = (bbox[2], bbox[3])
    center_bottomleft = (bbox[0], bbox[1])

    single_top_bottomright = (single_top.xmax, single_top.ymin)
    single_top_right_bottomleft = (single_top_right.xmin, single_top_right.ymin)
    single_right = (single_right.xmin, single_right.ymax)

    ## center_topright shared point : single_top[bottomright], single_top_right[bottomleft], single_right[topleft]
    assert (
        center_topright == single_top_bottomright
    ), "center_topright==single_top_bottomright"
    assert (
        center_topright == single_top_right_bottomleft
    ), "center_topright==single_top_right_bottomleft"
    assert center_topright == single_right, "center_topright==single_right"

    ## center_bottomleft shared point : single_bottom[topleft], single_bottom_left[topright], single_left[bottomright]
    single_bottom_topleft = (single_bottom.xmin, single_bottom.ymax)
    single_bottom_left_topright = (single_bottom_left.xmax, single_bottom_left.ymax)
    single_left_bottomright = (single_left.xmax, single_left.ymin)

    assert (
        center_bottomleft == single_bottom_topleft
    ), "center_bottomleft==single_bottom_topright"
    assert (
        center_bottomleft == single_bottom_left_topright
    ), "center_bottomleft==single_bottom_left_bottomright"
    assert (
        center_bottomleft == single_left_bottomright
    ), "center_bottomleft==single_left_bottomright"

    ## outer_topright shared point, single_top_right[topright]
    ## outer_bottomleft shared point, single_bottom_left[bottomleft]

    bbox_outer = ret.outer_rect.bbox
    outer_topright = (bbox_outer[2], bbox_outer[3])
    outer_bottomleft = (bbox_outer[0], bbox_outer[1])

    single_top_right_topright = (single_top_right.xmax, single_top_right.ymax)
    single_bottom_left_bottomleft = (single_bottom_left.xmin, single_bottom_left.ymin)

    assert (
        outer_topright == single_top_right_topright
    ), "outer_topright==single_top_right_topright"
    assert (
        outer_bottomleft == single_bottom_left_bottomleft
    ), "outer_bottomleft==single_bottom_left_bottomleft"


def test_decode_range():
    lat, lng, lat_err, lng_err = pgh.decode_exactly("wydbb")

    bias_point = (lat + lat_err * 1.1, lng + lng_err * 1.1)
    bias_geohash = pgh.encode(bias_point[0], bias_point[1], precision=5)
    assert bias_geohash != "wydbb"
    bias_point = (lat + lat_err * 0.9, lng + lng_err * 0.9)
    bias_geohash = pgh.encode(bias_point[0], bias_point[1], precision=5)
    assert bias_geohash == "wydbb"
