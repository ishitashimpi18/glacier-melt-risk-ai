"""
04_hydrology_link.py

Convert glacier mass balance into hydrological runoff contribution.
"""

import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
IN_FILE = "data/processed/glacier_ml_dataset.csv"
OUT_FILE = "data/processed/glacier_hydrology.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(IN_FILE)

print("Loaded ML dataset:", df.shape)

# -----------------------------
# CLEAN MASS CHANGE
# -----------------------------
# Only negative mass change contributes to meltwater runoff
df["melt_m"] = df["mass_change"].clip(upper=0).abs()

# -----------------------------
# COMPUTE RUNOFF
# -----------------------------
# area_km2 → m² = * 1e6
df["glacier_runoff_m3"] = df["melt_m"] * df["area_km2"] * 1e6

# -----------------------------
# OPTIONAL: Normalize runoff (useful for ML)
# -----------------------------
df["runoff_mm"] = df["melt_m"] * 1000  # meters → mm

# -----------------------------
# FINAL COLUMNS
# -----------------------------
final = df[[
    "glacier_id",
    "year",
    "area_km2",
    "temp_mean",
    "prec_mean",
    "srad_mean",
    "mass_change",
    "glacier_runoff_m3",
    "runoff_mm"
]]

print("Final hydrology rows:", final.shape)
print(final.head())

# -----------------------------
# SAVE
# -----------------------------
os.makedirs("data/processed", exist_ok=True)
final.to_csv(OUT_FILE, index=False)

print("✅ glacier_hydrology.csv created successfully")
