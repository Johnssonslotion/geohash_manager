"""
geohash 를 처리하기 위한 단위 함수들 주로 class 변수를 통한 설정을 통해 사용한다.
"""
from math import radians, sin, cos, atan2, sqrt
import math
from typing import Union
import pygeohash as pgh
from shapely.geometry import Polygon, Point, MultiPolygon

from geohash_manager.model.shape_model import CircleShape, RectShape
from tqdm import tqdm
import logging


class GeoUtils:
    """
    Function naming rule
    변경에 대해서 : "A_B" , A에서 B로 변경시, input A return B
    만약 A가 _ 를 포함한다면, _ 대신 to 사용하고 camel case로 표현한다.

    단일 값에 대해서는 get_ 을 붙인다.
    ## lat, lng = True lng, lat = False
    """

    limit_procision = 10
    precision = 5
    latlng_switch = False  ## 기본값은 lng lat

    direction_info = {
        "top": {"n": 1, "e": 0},
        "bottom": {"n": -1, "e": 0},
        "left": {"n": 0, "e": -1},
        "right": {"n": 0, "e": 1},
        "topleft": {"n": 1, "e": -1},
        "topright": {"n": 1, "e": 1},
        "bottomleft": {"n": -1, "e": -1},
        "bottomright": {"n": -1, "e": 1},
        "all": {"n": 0, "e": 0},
    }

    @classmethod
    def geohash_rect(cls, geohash):
        """
        single geohash to rect polygon
        :return geohashset, polygon
        """
        assert geohash is not None, "geohash is None"
        assert isinstance(geohash, str), "geohash is not str"
        assert len(geohash) > 0, "geohash is empty"

        lat, lon, lat_err, lon_err = pgh.decode_exactly(geohash)
        ## from lat lon lat_err lon_err to xmin, ymin, xmax, ymax
        xmin = lon - lon_err
        xmax = lon + lon_err
        ymin = lat - lat_err
        ymax = lat + lat_err
        obj = RectShape(bbox=(xmin, ymin, xmax, ymax))
        return obj

    @staticmethod
    def get_distance(cls, **kwargs):
        """
        두 지점의 위도, 경도를 입력받아 거리를 반환하는 함수
        확장: point_1, point_2, xmin, ymin, xmax, ymax 입력받아 거리를 반환하는 함수
        :param lat1: 지점1 위도
        :param lon1: 지점1 경도
        :param lat2: 지점2 위도
        :param lon2: 지점2 경도
        :return: 두 지점 사이의 거리
        """
        # TODO 연산 속도 개선을 위한 cpython으로 migration 필요 혹은 해당 적용된 라이브러리 사용

        point_1 = kwargs.get("point_1", None)
        point_2 = kwargs.get("point_2", None)

        lat1 = kwargs.get("lat1", None)
        lon1 = kwargs.get("lon1", None)
        lat2 = kwargs.get("lat2", None)
        lon2 = kwargs.get("lon2", None)

        xmin = kwargs.get("xmin", None)
        ymin = kwargs.get("ymin", None)
        xmax = kwargs.get("xmax", None)
        ymax = kwargs.get("ymax", None)

        if point_1 and point_2:
            lat1, lon1 = point_1
            lat2, lon2 = point_2
        if lat1 and lon1 and lat2 and lon2:
            pass
        elif xmin and ymin and xmax and ymax:
            lat1 = ymin
            lon1 = xmin
            lat2 = ymax
            lon2 = xmax

        R = 6373.0
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        d_lon = lon2 - lon1
        d_lat = lat2 - lat1

        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    @classmethod
    def subhash(cls, geohash, precision=None):
        """
        하위 hash를 반환하되 특별한 순서와 상관없이 반환한다.
        """
        assert geohash is not None, "geohash is None"
        assert isinstance(geohash, str), "geohash is not str"
        assert len(geohash) > 0, "geohash is empty"

        current_precision = len(geohash)
        base32_chars = "0123456789bcdefghjkmnpqrstuvwxyz"
        if precision is None:
            precision = cls.precision
        if current_precision == precision:  ## 최상위 해시라면
            return []
        else:
            ret = []
            for i in base32_chars:
                ret.append(geohash + str(i))
            return ret

    @classmethod
    def get_direction(point_1: Point, point_2: Point):
        """
        두 좌표를 입력받으면 좌표의 방향을 추산한다.
        """
        delta_x = point_2.x - point_1.x
        delta_y = point_2.y - point_1.y

        if delta_x > 0:
            if delta_y > 0:
                return "topright"
            elif delta_y < 0:
                return "bottomright"
            else:
                return "right"
        else:
            if delta_y > 0:
                return "topleft"
            elif delta_y < 0:
                return "bottomleft"
            else:
                return "left"

    @classmethod
    def neighbor(cls, **kwargs):
        """
        인접한 hash를 반환한다.

        이웃하는 문자열의 방향을 지정함으로써, 인접한 hash를 반환한다.
        입력한 위치를 latlng을 통해서 받을 경우, 해당 위치를 기준으로 경계가 가장 가까운 hash를 반환한다.
        """
        if "precision" in kwargs.keys():
            precision = kwargs["precision"]
        else:
            precision = cls.precision
        if "geohash" in kwargs.keys():
            geohash = kwargs["geohash"]
        elif "latlng" in kwargs.keys():
            latlng = kwargs["latlng"]
            geohash = pgh.encode(latlng[0], latlng[1], precision=precision)
        if "direction" in kwargs.keys():
            direction = kwargs["direction"]
        else:
            direction = "all"

        lat, lon, lat_err, lon_err = pgh.decode_exactly(geohash)
        lat_err *= 2
        lon_err *= 2

        # 이웃하는 문자열의 위치 정보를 계산합니다.
        n_delta = cls.direction_info[direction]["n"]
        e_delta = cls.direction_info[direction]["e"]
        neighbor_lat = lat + n_delta * lat_err
        neighbor_lon = lon + e_delta * lon_err

        # 이웃하는 문자열의 Geohash 문자열을 생성합니다.

        neighbor_geohash = pgh.encode(neighbor_lat, neighbor_lon, precision=precision)
        # 결과를 반환합니다.
        return neighbor_geohash

    @classmethod
    def cover_geohash(cls, target_polygon: Union[Polygon, MultiPolygon], precision):
        """
        precision을 기준으로 target_polygon을 덮는 geohash를 반환한다.
        subhash를 사용하지 않고 동일한 수준으로 반환한다.
        """

        assert target_polygon is not None, "target_polygon is None"
        assert isinstance(
            target_polygon, Union[Polygon, MultiPolygon]
        ), "target_polygon is not Polygon"
        if precision is None:
            precision = cls.precision

        geohash_set = set()

        ## from polygon to geohash rect sets
        target_edge = target_polygon.bounds  ## xmin,ymin,xmax,ymax
        init_edge_geohash = pgh.encode(target_edge[1], target_edge[0], precision)
        end_edge_geohash = pgh.encode(target_edge[3], target_edge[2], precision)

        y_min_adj, x_min_adj, y_err, x_err = pgh.decode_exactly(
            init_edge_geohash
        )  ## adjust xy_min to geohash
        y_max_adj, x_max_adj, y_err, x_err = pgh.decode_exactly(
            end_edge_geohash
        )  ## adjust xy_max to geohash

        if init_edge_geohash == end_edge_geohash:
            geohash_set.add(init_edge_geohash)
            return geohash_set

        x_count = (x_max_adj - x_min_adj) / (2 * x_err)
        y_count = (y_max_adj - y_min_adj) / (2 * y_err)

        for i in range(int(x_count)):
            for j in range(int(y_count)):
                geohash_set.add(
                    pgh.encode(
                        y_min_adj + 2 * j * y_err,
                        x_min_adj + 2 * i * x_err,
                        precision=precision,
                    )
                )
        ## remove geohash that is not in polygon

        for ii, geohash in enumerate(geohash_set.copy()):
            rectshape = cls.geohash_rect(geohash)
            polygon = rectshape.polygon
            if not target_polygon.intersection(polygon):
                geohash_set.remove(geohash)
        return geohash_set

    @classmethod
    def geohash_set_to_polygon(cls, geohash_set):
        ret = []
        for i in geohash_set:
            ret.append(cls.geohash_rect(i).polygon)
        return ret

    @classmethod
    def xyr_circle(cls, **kwargs):
        """
        input : lat, lng, radius,
        output : polygon,
        """
        center = kwargs.get("position", None)
        center = kwargs.get("center", None)
        ##
        lat = kwargs.get("lat", None)
        lng = kwargs.get("lng", None)
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        r = kwargs.get("r", None)
        radius = kwargs.get("radius", None)

        if radius or r == None:
            raise NotImplementedError("radius is not implemented")
        else:
            radius = radius or r
        if center:
            circle = CircleShape(center=center, radius=radius)
        elif lat and lng:
            circle = CircleShape(center=(lng, lat), radius=radius)
        elif x and y:
            circle = CircleShape(center=(x, y), radius=radius)
        else:
            raise Exception("position or center should be defined")
        return circle

    @classmethod
    def bbox_rect(cls, **kwargs):
        """
        입력방법,
        튜플로 입력하거나, 각각입력하거나,
        - bbox=(xmin,ymin,xmax,ymax)
        - xmin,ymin,xmax,ymax
        - lng1,lat1,lng2,lat2
        return : RectShape
        """
        bbox = kwargs.get("bbox", None)
        xmin = kwargs.get("xmin", None)
        lat1 = kwargs.get("lat1", None)
        ymin = kwargs.get("ymin", None)
        lng1 = kwargs.get("lng1", None)
        xmax = kwargs.get("xmax", None)
        lat2 = kwargs.get("lat2", None)
        ymax = kwargs.get("ymax", None)
        lng2 = kwargs.get("lng2", None)

        if bbox:
            rect = RectShape(bbox=bbox)
        elif xmin and ymin and xmax and ymax:
            rect = RectShape(bbox=(xmin, ymin, xmax, ymax))
        elif lng1 and lat1 and lng2 and lat2:
            rect = RectShape(bbox=(lng1, lat1, lng2, lat2))
        else:
            raise Exception("bbox or lng1,lat1,lng2,lat2 should be defined")
        return rect

    @staticmethod
    def compute_point_at_distance_and_bearing(x, y, distance, bearing):
        R = 6371000  # Earth radius in meters
        delta = distance / R

        theta = math.radians(bearing)
        phi1 = math.radians(y)
        lambda1 = math.radians(x)

        phi2 = math.asin(
            math.sin(phi1) * math.cos(delta)
            + math.cos(phi1) * math.sin(delta) * math.cos(theta)
        )
        lambda2 = lambda1 + math.atan2(
            math.sin(theta) * math.sin(delta) * math.cos(phi1),
            math.cos(delta) - math.sin(phi1) * math.sin(phi2),
        )
        return math.degrees(lambda2), math.degrees(phi2)

    @classmethod
    def generate_samples_for_circle(cls, x, y, radians, samples):
        """
        x,y : center
        radians : radius
        samples : number of samples
        """
        ret = []
        for i in range(samples):
            bearing = 360 / samples * i
            ret.append(
                GeoUtils.compute_point_at_distance_and_bearing(x, y, radians, bearing)
            )
        return ret
