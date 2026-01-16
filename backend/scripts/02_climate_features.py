"""
02_climate_features.py
Extract climate variables (precip, temp, solar radiation)
from WorldClim GeoTIFFs for each glacier
"""

import os
import pandas as pd
import rasterio
from rasterio.sample import sample_gen

# -----------------------------
# PATHS
# -----------------------------
RAW = "data/raw/climate"
IN_GLACIER = "data/processed/glacier_master_with_area.csv"
OUT = "data/processed"

PREC_DIR = os.path.join(RAW, "wc2.1_2.5m_prec")
TEMP_DIR = os.path.join(RAW, "wc2.1_2.5m_tavg")
SRAD_DIR = os.path.join(RAW, "wc2.1_2.5m_srad")

# -----------------------------
# LOAD GLACIERS
# -----------------------------
df = pd.read_csv(IN_GLACIER)

# Rasterio expects (lon, lat)
coords = list(zip(df["lon"], df["lat"]))

# -----------------------------
# FUNCTION TO SAMPLE RASTERS
# -----------------------------
def sample_mean(folder):
    values = []

    tif_files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".tif")
    ])

    for tif in tif_files:
        with rasterio.open(tif) as src:
            samples = [v[0] for v in src.sample(coords)]
            values.append(samples)

    # mean across months
    return pd.DataFrame(values).mean().values

# -----------------------------
# EXTRACT CLIMATE VARIABLES
# -----------------------------
print("Extracting precipitation...")
df["prec_mean"] = sample_mean(PREC_DIR)

print("Extracting temperature...")
df["temp_mean"] = sample_mean(TEMP_DIR)

print("Extracting solar radiation...")
df["srad_mean"] = sample_mean(SRAD_DIR)

# -----------------------------
# CLEAN
# -----------------------------
df = df.dropna(subset=["prec_mean", "temp_mean", "srad_mean"])

print(f"Final glacier-climate rows: {len(df)}")

# -----------------------------
# SAVE
# -----------------------------
os.makedirs(OUT, exist_ok=True)

df[[
    "glacier_id",
    "lat",
    "lon",
    "area_km2",
    "prec_mean",
    "temp_mean",
    "srad_mean"
]].to_csv(
    os.path.join(OUT, "climate_features.csv"),
    index=False
)

print("✅ climate_features.csv created successfully")
