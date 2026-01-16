import pandas as pd
import re

# -----------------------------
# Paths
# -----------------------------
GLACIER_MASTER_PATH = "data/processed/glacier_master.csv"
RGI_ATTR_PATH = "data/raw/mass_balance/RGI2000-v7.0-G-global-attributes.csv"
OUTPUT_PATH = "data/processed/glacier_master_with_area.csv"

print("Loading glacier master...")
gm = pd.read_csv(GLACIER_MASTER_PATH)

print("Loading RGI global attributes...")
rgi = pd.read_csv(RGI_ATTR_PATH)

print("Glacier master shape:", gm.shape)
print("RGI attributes shape:", rgi.shape)

# -----------------------------
# 1. Extract numeric glacier ID
# -----------------------------
def extract_numeric_id(rgi_id):
    """
    Extracts 14.03456 from:
    RGI2000-v5.0-14.03456
    RGI2000-v7.0-G-14.03456
    """
    if pd.isna(rgi_id):
        return None
    match = re.search(r"(\d+\.\d+)", str(rgi_id))
    return match.group(1) if match else None

gm["gid"] = gm["glacier_id"].apply(extract_numeric_id)
rgi["gid"] = rgi["rgi_id"].apply(extract_numeric_id)

# -----------------------------
# 2. Keep only what we need
# -----------------------------
rgi_area = rgi[["gid", "area_km2"]].dropna()

# If duplicates exist, take mean area (safe)
rgi_area = rgi_area.groupby("gid", as_index=False)["area_km2"].mean()

# -----------------------------
# 3. Merge
# -----------------------------
gm = gm.merge(
    rgi_area,
    on="gid",
    how="left"
)

# -----------------------------
# 4. Replace area_km2
# -----------------------------
gm["area_km2"] = gm["area_km2_y"]
gm.drop(columns=["area_km2_x", "area_km2_y", "gid"], inplace=True)

# -----------------------------
# 5. Check results
# -----------------------------
print("\nArea statistics after merge:")
print(gm["area_km2"].describe())

print("\nMissing area count:", gm["area_km2"].isna().sum())

# -----------------------------
# 6. Save
# -----------------------------
gm.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ glacier_master_with_area.csv created successfully")
