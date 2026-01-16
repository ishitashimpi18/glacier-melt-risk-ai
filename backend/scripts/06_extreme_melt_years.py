"""
06_extreme_melt_years.py
Identify extreme glacier melt years using basin-scale runoff anomalies
"""

import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = "data/processed/basin_runoff_timeseries.csv"
OUT_DIR = "data/processed"
OUT_FILE = os.path.join(OUT_DIR, "extreme_melt_years.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)

print("Loaded basin runoff data:", df.shape)

# -----------------------------
# LONG-TERM STATISTICS
# -----------------------------
mean_runoff = df["basin_runoff_mm"].mean()
std_runoff = df["basin_runoff_mm"].std()

print(f"Mean basin runoff (mm): {mean_runoff:.3f}")
print(f"Std deviation (mm): {std_runoff:.3f}")

# -----------------------------
# ANOMALIES & Z-SCORE
# -----------------------------
df["runoff_anomaly_mm"] = df["basin_runoff_mm"] - mean_runoff
df["z_score"] = df["runoff_anomaly_mm"] / std_runoff

# -----------------------------
# CLASSIFY EXTREMES
# -----------------------------
def classify_melt(z):
    if z >= 2:
        return "Extreme Melt"
    elif z >= 1:
        return "High Melt"
    elif z <= -1:
        return "Low Melt"
    else:
        return "Normal"

df["melt_category"] = df["z_score"].apply(classify_melt)

# -----------------------------
# SORT BY SEVERITY
# -----------------------------
df_sorted = df.sort_values("z_score", ascending=False)

# -----------------------------
# SAVE
# -----------------------------
os.makedirs(OUT_DIR, exist_ok=True)
df_sorted.to_csv(OUT_FILE, index=False)

print("✅ extreme_melt_years.csv created")
print("\nTop extreme melt years:")
print(
    df_sorted[["year", "basin_runoff_mm", "z_score", "melt_category"]].head(10)
)
