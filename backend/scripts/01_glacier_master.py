import geopandas as gpd
import pandas as pd
import os

RAW = "data/raw/mass_balance"
OUT = "data/processed"

WEST = os.path.join(
    RAW,
    "RGI2000-v7.0-I-14_south_asia_west",
    "RGI2000-v7.0-I-14_south_asia_west.shp"
)

EAST = os.path.join(
    RAW,
    "RGI2000-v7.0-I-15_south_asia_east",
    "RGI2000-v7.0-I-15_south_asia_east.shp"
)

print("Loading glacier geometries...")
gdf = pd.concat(
    [gpd.read_file(WEST), gpd.read_file(EAST)],
    ignore_index=True
)

gdf.columns = gdf.columns.str.lower()

# ---- AREA (projected CRS) ----
gdf_proj = gdf.to_crs(epsg=6933)
area_km2 = gdf_proj.geometry.area / 1e6

# ---- LAT / LON (geographic CRS) ----
gdf_ll = gdf.to_crs(epsg=4326)
lon = gdf_ll.geometry.centroid.x
lat = gdf_ll.geometry.centroid.y

# ---- FINAL TABLE ----
glacier_master = pd.DataFrame({
    "glacier_id": gdf["rgi_id"],
    "lat": lat,
    "lon": lon,
    "area_km2": area_km2,
    "region": "Himalayas"
})

print(glacier_master["area_km2"].describe())

os.makedirs(OUT, exist_ok=True)
glacier_master.to_csv(
    os.path.join(OUT, "glacier_master.csv"),
    index=False
)

print("✅ glacier_master.csv created with REAL area values")

