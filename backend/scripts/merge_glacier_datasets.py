import os
import pandas as pd

# ===============================
# CORRECT PROJECT ROOT (2 levels up)
# ===============================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUT_FILE = os.path.join(DATA_DIR, "glacier_explorer_merged.csv")

print(f"📂 Script dir: {SCRIPT_DIR}")
print(f"📂 Backend dir: {BACKEND_DIR}")
print(f"📂 Project root: {PROJECT_ROOT}")
print(f"📂 Data directory: {DATA_DIR}")

# ===============================
# 1. LOAD BASE GLACIER DATA
# ===============================
base_path = os.path.join(DATA_DIR, "glacier_master_with_area.csv")
assert os.path.exists(base_path), f"❌ File not found: {base_path}"

base = pd.read_csv(base_path)
base.columns = base.columns.str.lower()

# Ensure lat/lon
if "lat" not in base.columns:
    if "latitude" in base.columns:
        base.rename(columns={"latitude": "lat"}, inplace=True)
    elif "cenlat" in base.columns:
        base.rename(columns={"cenlat": "lat"}, inplace=True)

if "lon" not in base.columns:
    if "longitude" in base.columns:
        base.rename(columns={"longitude": "lon"}, inplace=True)
    elif "cenlon" in base.columns:
        base.rename(columns={"cenlon": "lon"}, inplace=True)

assert "lat" in base.columns and "lon" in base.columns, "❌ lat/lon missing"

print(f"✅ Base glaciers loaded: {len(base)}")

# ===============================
# 2. LOAD OTHER DATASETS
# ===============================
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    assert os.path.exists(path), f"❌ Missing file: {filename}"
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    print(f"✅ Loaded {filename} ({len(df)})")
    return df

climate = load_csv("climate_features.csv")
melt = load_csv("extreme_melt_years.csv")
flood = load_csv("flood_risk_index.csv")
future = load_csv("future_melt_projection.csv")

# ===============================
# 3. LATEST RECORDS
# ===============================
if "year" in melt.columns:
    melt = melt.sort_values("year").groupby("basin").tail(1)

if "year" in flood.columns:
    flood = flood.sort_values("year").groupby("basin").tail(1)

if "year" in future.columns:
    future = future.sort_values("year").groupby("glacier_id").tail(1)

# ===============================
# 4. MERGE (BASE FIRST)
# ===============================
df = base.merge(climate, on="glacier_id", how="left")
df = df.merge(future, on="glacier_id", how="left")

if "basin" in df.columns:
    df = df.merge(
        melt[["basin", "melt_category"]],
        on="basin",
        how="left"
    )
    df = df.merge(
        flood[["basin", "flood_risk_level"]],
        on="basin",
        how="left"
    )
else:
    df["melt_category"] = "Unknown"
    df["flood_risk_level"] = "Unknown"

# ===============================
# 5. SAFE DEFAULTS
# ===============================
for col in ["temp_mean", "predicted_melt", "area_km2"]:
    if col not in df.columns:
        df[col] = None

df["melt_category"] = df["melt_category"].fillna("Unknown")
df["flood_risk_level"] = df["flood_risk_level"].fillna("Unknown")

# ===============================
# 6. GLACIER-LEVEL RISK LOGIC
# ===============================
def compute_risk(row):
    score = 0

    if pd.notna(row["temp_mean"]):
        if row["temp_mean"] > 0:
            score += 2
        elif row["temp_mean"] > -1:
            score += 1

    if pd.notna(row["predicted_melt"]):
        if row["predicted_melt"] < -0.6:
            score += 2
        elif row["predicted_melt"] < -0.3:
            score += 1

    if pd.notna(row["area_km2"]) and row["area_km2"] < 5:
        score += 1

    if row["melt_category"] == "Extreme Melt":
        score += 2
    if row["flood_risk_level"] == "High Risk":
        score += 2

    if score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"

df["risk_level"] = df.apply(compute_risk, axis=1)

# ===============================
# 7. EXPORT
# ===============================
final_cols = [
    "glacier_id",
    "lat",
    "lon",
    "area_km2",
    "temp_mean",
    "melt_category",
    "flood_risk_level",
    "predicted_melt",
    "risk_level"
]

# ===============================
# FIX LAT / LON AFTER MERGES
# ===============================
if "lat" not in df.columns:
    if "lat_x" in df.columns:
        df["lat"] = df["lat_x"]
    elif "latitude" in df.columns:
        df["lat"] = df["latitude"]

if "lon" not in df.columns:
    if "lon_x" in df.columns:
        df["lon"] = df["lon_x"]
    elif "longitude" in df.columns:
        df["lon"] = df["longitude"]

# Drop duplicate coordinate columns if present
df.drop(
    columns=[c for c in ["lat_x", "lat_y", "lon_x", "lon_y"] if c in df.columns],
    inplace=True,
    errors="ignore"
)

# HARD SAFETY CHECK
assert "lat" in df.columns and "lon" in df.columns, "❌ lat/lon still missing after merge"

df_final = df[final_cols].dropna(subset=["lat", "lon"])
df_final.to_csv(OUT_FILE, index=False)

print("🎉 MERGE COMPLETE")
print(f"📄 Saved: {OUT_FILE}")
print(df_final["risk_level"].value_counts())
