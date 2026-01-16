"""
05_basin_aggregation.py

Aggregate glacier meltwater runoff by basin / region and year.
Converts glacier-scale melt to regional (river-basin-scale) contribution.
"""

import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
IN_FILE = "data/processed/glacier_hydrology.csv"
OUT_DIR = "data/processed"
OUT_FILE = os.path.join(OUT_DIR, "basin_runoff_timeseries.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(IN_FILE)

print("Loaded glacier hydrology data:", df.shape)

# -----------------------------
# BASIC SANITY CHECK
# -----------------------------
required_cols = [
    "glacier_id",
    "year",
    "area_km2",
    "glacier_runoff_m3",
    "runoff_mm"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"❌ Missing required columns: {missing}")

# -----------------------------
# ADD BASIN / REGION COLUMN
# -----------------------------
# (You currently have Himalayas only, but this allows future expansion)
df["basin"] = "Himalayas"

# -----------------------------
# AGGREGATE BY BASIN + YEAR
# -----------------------------
basin_agg = (
    df.groupby(["basin", "year"])
    .agg(
        total_glacier_runoff_m3=("glacier_runoff_m3", "sum"),
        mean_runoff_mm=("runoff_mm", "mean"),
        glacier_count=("glacier_id", "nunique"),
        total_glacier_area_km2=("area_km2", "sum")
    )
    .reset_index()
)

# -----------------------------
# OPTIONAL: NORMALIZED RUNOFF
# -----------------------------
# Basin-wide runoff depth (mm)
basin_agg["basin_runoff_mm"] = (
    basin_agg["total_glacier_runoff_m3"]
    / (basin_agg["total_glacier_area_km2"] * 1e6)
)

# -----------------------------
# SAVE
# -----------------------------
os.makedirs(OUT_DIR, exist_ok=True)
basin_agg.to_csv(OUT_FILE, index=False)

# -----------------------------
# SUMMARY
# -----------------------------
print("✅ basin_runoff_timeseries.csv created")
print(basin_agg.head())
print("\nFinal basin dataset shape:", basin_agg.shape)
