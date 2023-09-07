from collections import deque
import logging
import pygeohash as pgh
import numpy as np
import rtree as rt
from typing import Optional, List, Tuple, Union
from geohash_manager.model.shape_model import CircleShape, Geohashes, GeohashObject
from geohash_manager.utils.geo_utils import GeoUtils
from shapely.geometry import Polygon, Point, LineString, LinearRing


class GeohashManager(GeoUtils):
    """
    Geohash를 관리하기 위한 클래스
    이 클래스를 통해서 Geohash를 관리하고, Geohash를 통해서 공간을 관리할 수 있습니다.

    설계가 필요한 기능 정의하기
    - 다중검색을 위한 Geohash 관리

    Attributes:
        geohash_precision (int): Geohash의 정밀도를 나타냅니다.
        geohash_index (rtree.index): Geohash를 관리하기 위한 R-tree 인덱스입니다.

    비고 : ClassMethod를 따로 관리 GeoUtils로,
    """

    def __init__(self, **kwargs):
        ## set geohash precision smallest limit (default: 8)
        ## geohash precision limit: 4 ~ 8
        self.precision = kwargs.get("precision", 4)
        self.limits = kwargs.get("limits", 6)
        self.position = kwargs.get("positions", None)
        self.debug = kwargs.get("debug", False)
        self.tracert = []
        if self.position is not None:
            self.tracert.append(self.position)
        self.mode = kwargs.get("mode", "tracker")
        ## logger
        self.logger_name = kwargs.get("logger", "geohash_manager")
        self.logger = logging.getLogger(self.logger_name)
        sh = logging.StreamHandler()
        if self.debug:
            sh.setLevel(logging.DEBUG)
        else:
            sh.setLevel(logging.INFO)
        self.logger.addHandler(sh)
        ##
        self.ret = []
        self.init_shape = None

    def add_position(self, latlng: Tuple[float, float]):
        self.tracert.append(latlng)
        ## TODO : 직전 포지션과 거리가 멀 경우 tracert reset // 인접하지 않을 경우
        if len(self.tracert) > 2:
            self.tracert.pop(0)
        self.positions = latlng

    def neighbors(self, **kwargs):
        """
        class 변수에 의해 정의된 neighbor 함수를 기초로, 현재 위치를 기준으로 인접한 geohash를
        반환합니다.
        가까울수록 높은 우선순위를 가집니다.
        return :
        dict
        - geohashes : geohash obj[geohash,bbox]
        """
        ret = {"geohashes": [], "order": []}
        position = kwargs.get("position", None)
        precision = kwargs.get("precision", None)
        if precision is None:
            precision = self.precision
        if position is not None:
            position, geohash, bias = self.position_geohashobj(
                position=position, precision=precision
            )
        else:
            geohash = kwargs.get("geohash", None)
            bias = kwargs.get("bias", None)
            assert geohash is not None, "geohash or position must be not None"

        assert type(geohash) == GeohashObject

        if bias == "topright":
            num_rotate = 1
        elif bias == "right":
            num_rotate = 2
        elif bias == "bottomright":
            num_rotate = 3
        elif bias == "bottom":
            num_rotate = 4
        elif bias == "bottomleft":
            num_rotate = 5
        elif bias == "left":
            num_rotate = 6
        elif bias == "topleft":
            num_rotate = 7
        else:
            num_rotate = 0

        def rotate(lst, k):
            k = k % len(lst)
            lst = lst[k:] + lst[:k]
            return lst

        # if direction == "all":
        ## 시계방향임에 따라, 시작지점을 조정함
        directions = [
            "top",
            "topright",
            "right",
            "bottomright",
            "bottom",
            "bottomleft",
            "left",
            "topleft",
        ]

        # neighbor_geohashes = []
        directions = rotate(directions, num_rotate)
        for direction in directions:
            ret["order"].append(direction)
            ret["geohashes"].append(
                self.neighber(geohash=geohash, precision=precision, direction=direction)
            )
        return Geohashes(**ret)

    def neighber(self, **kwargs):
        ## 현재 상황에 따라 인접한 geohash를 반환합니다.
        kwargs["position"] = self.position
        kwargs["precision"] = self.precision
        return super().neighbor(**kwargs)

    def xyr_to_rects(self, **kwargs):
        """
        1. 기본적인 xyr을 받아서 polygon을 생성
        2. polygon의 bound 에 맞는 geohash를 반환
        3. geohash를 기준으로 Rect을 받고, Rect의 polygon을 반환
        4. cover하는 영역을 확인하고, 해당 영역에 해당하는 geohash를 반환

        # 겹치는 영역이 5퍼     미만이면 제외
        """
        threshold = kwargs.get("threshold", 0.5)

        if self.init_shape is None:
            sample = kwargs.get("sample", 100)
            cir = self.xyr_circle(**kwargs)
            arr = self.generate_samples_for_circle(cir.x, cir.y, cir.radius, sample)
            self.init_shape = Polygon(arr)
        area_geohash_set = self.cover_geohash(
            target_polygon=self.init_shape, precision=self.precision
        )
        ## 넓이가 너무 큰 경우 - subhash로 분할
        ## 어떻게 넓이가 큰지 확인? -> rect - init_polygon 이 50% 미만인 경우, (subhash는 32개로 분할됨, 3.125)

        div_candidate = deque()
        div_candidate.extend(area_geohash_set)
        while len(div_candidate) > 0:
            i = div_candidate.pop()
            rect = self.geohash_rect(i)
            difference_area = rect.polygon.difference(self.init_shape).area
            ratio = difference_area / rect.polygon.area
            if ratio != 1:
                if ratio < threshold:
                    self.logger.debug(
                        f"\n id :{i}  ratio : {ratio}, diff_area : {difference_area}"
                    )
            if ratio == 1:
                continue  ## 겹치는 영역이 없음
            if ratio != 1:
                if ratio < threshold:
                    self.ret.append(rect)
                elif len(i) <= self.limits:
                    div_candidate.extend(self.subhash(i, self.limits))
        return self.ret

    def rect_to_rects(self, **kwargs):
        """
        입력 받은 후에 동일하게 처리

        """
        threshold = kwargs.get("threshold", 0.5)

        if self.init_shape is None:
            self.init_shape = self.bbox_rect(**kwargs).polygon
        area_geohash_set = self.cover_geohash(
            target_polygon=self.init_shape, precision=self.precision
        )
        geohash_set = []
        div_candidate = deque()
        div_candidate.extend(area_geohash_set)
        gh = None
        while len(div_candidate) > 0:
            i = div_candidate.pop()
            rect = self.geohash_rect(i)
            difference_area = rect.polygon.difference(self.init_shape).area
            ratio = difference_area / rect.polygon.area
            if ratio != 1:
                if ratio < threshold:
                    self.logger.debug(
                        f"\n id :{i}  ratio : {ratio}, diff_area : {difference_area}"
                    )
            if ratio == 1:
                continue  ## 겹치는 영역이 없음
            if ratio != 1:
                if ratio < threshold:
                    self.ret.append(rect)
                    geohash_set.append(i)
                    # temp.append(i)
                elif len(i) < self.limits:
                    div_candidate.extend(self.subhash(i, self.limits))

            if ratio == 0:
                gh = i
        if len(self.ret) == 1:
            ## 1개의 geohash만 반환되는 경우, 해당 geohash의 subhash를 반환
            ret_geohash = self.subhash(gh, self.limits)
            ret = [self.geohash_rect(i) for i in ret_geohash]
            return ret, ret_geohash
        else:
            return self.ret, geohash_set
