import pandas as pd
import glob
import re
import os

# -----------------------------
# PATHS
# -----------------------------
CLIMATE_FILE = "data/processed/climate_features.csv"
WGMS_FOLDER = "data/raw/mass_balance/wgms"
OUT_FILE = "data/processed/glacier_ml_dataset.csv"

# -----------------------------
# LOAD CLIMATE
# -----------------------------
climate = pd.read_csv(CLIMATE_FILE)

# 🔑 Extract REGION.NUMBER from RGI v7
# RGI2000-v7.0-I-15-03456 → 15.03456
climate["glacier_key"] = climate["glacier_id"].str.extract(
    r"I-(\d{2})-(\d+)"
).agg(".".join, axis=1)

print("Climate rows:", climate.shape)
print("Sample climate keys:", climate["glacier_key"].dropna().head())

# -----------------------------
# LOAD ALL WGMS FILES
# -----------------------------
wgms_files = glob.glob(
    os.path.join(WGMS_FOLDER, "*MEAN-CAL-mass-change-series*_obs_unobs.csv")
)

wgms_list = []
for f in wgms_files:
    print("Loading:", os.path.basename(f))
    wgms_list.append(pd.read_csv(f))

wgms = pd.concat(wgms_list, ignore_index=True)
print("WGMS combined shape:", wgms.shape)

# -----------------------------
# FIND CORRECT ID COLUMN
# -----------------------------
id_col = None
for c in wgms.columns:
    if c.lower() in ["rgiid", "rgid"]:
        id_col = c
        break

if id_col is None:
    raise ValueError("❌ No RGI ID column found in WGMS")

print("Using WGMS ID column:", id_col)

# 🔑 Extract REGION.NUMBER
# RGI60-15.03456 → 15.03456
wgms["glacier_key"] = wgms[id_col].str.extract(r"(\d{2}\.\d+)")

print("Sample WGMS keys:", wgms["glacier_key"].dropna().head())

# -----------------------------
# 🔥 MELT YEARS (ONLY 2000–2024)
# -----------------------------
year_cols = [
    c for c in wgms.columns
    if c.isdigit() and 2000 <= int(c) <= 2024
]

print("Selected year columns:", len(year_cols))
print("Year range:", min(year_cols), "-", max(year_cols))

wgms_long = wgms.melt(
    id_vars=["glacier_key"],
    value_vars=year_cols,
    var_name="year",
    value_name="mass_change"
)

wgms_long["year"] = wgms_long["year"].astype(int)

# -----------------------------
# MERGE
# -----------------------------
final = climate.merge(
    wgms_long,
    on="glacier_key",
    how="inner"
)

print("After merge shape:", final.shape)

# -----------------------------
# FINAL ML TABLE
# -----------------------------
final = final[[
    "glacier_id",
    "year",
    "area_km2",
    "temp_mean",
    "prec_mean",
    "srad_mean",
    "mass_change"
]]

final.dropna(inplace=True)

# -----------------------------
# SAVE
# -----------------------------
final.to_csv(OUT_FILE, index=False)

print("✅ glacier_ml_dataset.csv created")
print(final.head())
print("Final dataset shape:", final.shape)
