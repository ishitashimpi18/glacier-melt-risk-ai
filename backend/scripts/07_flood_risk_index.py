"""
07_flood_risk_index.py
Flood risk index from glacier melt and runoff
"""

import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = "data/processed/extreme_melt_years.csv"
OUT_DIR = "data/processed"
OUT_FILE = os.path.join(OUT_DIR, "flood_risk_index.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)
print("Loaded extreme melt years:", df.shape)

print("Available columns:")
print(df.columns.tolist())

# -----------------------------
# USE Z-SCORE AS RUNOFF ANOMALY
# -----------------------------
runoff_col = "z_score"

# Normalize Z-score to 0–1
df["runoff_norm"] = (
    (df[runoff_col] - df[runoff_col].min()) /
    (df[runoff_col].max() - df[runoff_col].min())
)

# -----------------------------
# MELT SCORE
# -----------------------------
melt_score = {
    "Low Melt": 0.2,
    "Normal": 0.4,
    "High Melt": 0.7,
    "Extreme Melt": 1.0
}

df["melt_score"] = df["melt_category"].map(melt_score)

# -----------------------------
# FLOOD RISK INDEX
# -----------------------------
df["flood_risk_index"] = (
    0.6 * df["runoff_norm"] +
    0.4 * df["melt_score"]
)

# -----------------------------
# CLASSIFICATION
# -----------------------------
def classify_risk(x):
    if x >= 0.75:
        return "High Risk"
    elif x >= 0.45:
        return "Moderate Risk"
    else:
        return "Low Risk"

df["flood_risk_level"] = df["flood_risk_index"].apply(classify_risk)

# -----------------------------
# SAVE
# -----------------------------
os.makedirs(OUT_DIR, exist_ok=True)

df[[
    "basin",
    "year",
    "melt_category",
    "z_score",
    "flood_risk_index",
    "flood_risk_level"
]].to_csv(OUT_FILE, index=False)

print("✅ Flood risk index created successfully")
print(df[["year", "flood_risk_level"]].head())
