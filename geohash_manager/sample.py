import geopandas as gpd
from tqdm import tqdm
from geohash_manager.main import GeohashManager


def generate_grid(f):
    f = gpd.read_file(f, encoding="cp949")
    f.set_crs(epsg=5179, inplace=True)
    f.to_crs(epsg=4326, inplace=True)
    f.to_file("./sample/geojson/ctprvn.geojson", driver="GeoJSON")

    # tqdm.pandas()
    # f["geohash_set"] = f["geometry"].progress_apply(
    #     lambda x: list(GeohashManager.cover_geohash(x, precision=6))
    # )
    # ff = f.explode("geohash_set", ignore_index=False)
    # ff["geometry_base"] = ff["geometry"]
    # ff.drop("geometry", axis=1, inplace=True)
    # ff["geometry"] = ff["geohash_set"].apply(
    #     lambda x: GeohashManager.geohash_rect(x).polygon
    # )
    # ff.to_file("./sample/geojson/ctprvn_grid.geojson", driver="GeoJSON")
    # print("done")


if __name__ == "__main__":
    path = "./sample/shp/ctprvn.shp"
    json_path = "./sample/geojson/ctprvn_grid.geojson"
    generate_grid(path)
    # f = gpd.read_file(json_path, encoding="cp949")
    # f.set_crs(epsg=4326, inplace=True)
    # print("check")
