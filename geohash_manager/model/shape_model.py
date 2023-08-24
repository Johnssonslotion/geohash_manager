from typing import List, Optional, TYPE_CHECKING, Any
from typing_extensions import Literal
from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    Field,
    field_validator,
    model_serializer,
    model_validator,
)


from shapely.geometry import Polygon, Point, LineString, LinearRing


class RectShape(BaseModel):
    """
    GEOJSON order : LNG LAT
    for normal rectangle shape gis data
    sw : south west
    ne : north east
    xmin : min longitude of rectangle, generally south west
    ymin : min latitude of rectangle, generally south west
    xmax : max longitude of rectangle, generally north east
    ymax : max latitude of rectangle, generally north east
    """

    ## 위도(lat) y축, 경도(lng) x축

    xmin: float = Field(
        validation_alias=AliasChoices("xmin", AliasPath("bbox", 0)),
        description="min longitude of rectangle, generally south west",
    )
    ymin: float = Field(
        validation_alias=AliasChoices("ymin", AliasPath("bbox", 1)),
        description="min latitude of rectangle, generally south west",
    )
    xmax: float = Field(
        validation_alias=AliasChoices("xmax", AliasPath("bbox", 2)),
        description="max longitude of rectangle, generally north east",
    )
    ymax: float = Field(
        validation_alias=AliasChoices("ymax", AliasPath("bbox", 3)),
        description="max latitude of rectangle, generally north east",
    )

    @model_validator(mode="after")
    def check_bbox(self, values):
        ## TODO : BBOX 로 입력받았을때 오류 있음
        if self.xmin.__class__.__name__ == "AliasChoices":
            return self
        if self.ymin > 90 or self.ymin < -90:  ## x = lng이어야 하는데, lat으로 입력 받았을때,
            lat = self.ymin
            lng = self.xmin
            self.xmin = lat
            self.ymin = lng
            ## swap
            return self
        if self.ymax > 90 or self.ymax < -90:
            lat = self.ymax
            lng = self.xmax
            self.xmax = lat
            self.ymax = lng
            return self
        if self.xmin > 180 or self.xmin < -180:
            raise ValueError("min lng must be in range [-180, 180]")
        if self.xmax > 180 or self.xmax < -180:
            raise ValueError("max lng must be in range [-180, 180]")
        return self

    @property
    def items(self):
        return (self.xmin, self.ymin, self.xmax, self.ymax)

    @property
    def polygon(self):
        xx = [self.xmin, self.xmax, self.xmax, self.xmin, self.xmin]
        yy = [self.ymin, self.ymin, self.ymax, self.ymax, self.ymin]
        return Polygon(zip(xx, yy))

    @model_serializer
    def serialize_model(self) -> str:
        return ",".join([str(i) for i in self.items])

    if TYPE_CHECKING:
        # Ensure type checkers see the correct return type
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
        ) -> str:
            ...


class CircleShape(BaseModel):
    """
    for circle shape gis data
    center : center of circle
    radius : radius of circle
    TODO : CircleType을 serialize 할수 있도록 {x,y,r}
    """

    x: Optional[float] = Field(
        validation_alias=AliasChoices("x", AliasPath("center", 0)),
        description="longitude",
    )
    y: Optional[float] = Field(
        validation_alias=AliasChoices("y", AliasPath("center", 1)),
        description="latitude",
    )
    radius: float = Field(description="radius of circle, unit is meter")

    @model_validator(mode="after")
    def check_center(self, values):
        if self.y >= 90 or self.y <= -90:  ## x = lng이어야 하는데, lat으로 입력 받았을때,
            self.y, self.x = self.x, self.y  ## swap
        if self.x >= 180 or self.x <= -180:
            raise ValueError("longitude must be in range [-180, 180]")
        return self

    @model_serializer
    def serialize(self):
        return {"x": self.x, "y": self.y, "radius": self.radius}

    ## 서큘러 import 이슈로 인해서 제외
    # @property
    # def polygon(self):
    #     """
    #     ref : https://scitools.org.uk/cartopy/docs/latest/reference/generated/cartopy.geodesic.Geodesic.html
    #     """
    #     arr = GeoUtils.generate_samples_for_circle(
    #         x=self.x, y=self.y, radius=self.radius, samples=100
    #     )
    #     return Polygon(arr)
