"""
07_climate_sensitivity.py
Spatial climate sensitivity of glacier melt
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import os

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = "data/processed/glacier_ml_dataset.csv"
OUT_DIR = "data/processed"

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)
print("Loaded ML dataset:", df.shape)

# -----------------------------
# AGGREGATE PER GLACIER
# -----------------------------
glacier_stats = (
    df.groupby("glacier_id")
    .agg(
        mean_melt=("mass_change", "mean"),
        temp=("temp_mean", "first"),
        prec=("prec_mean", "first"),
        srad=("srad_mean", "first"),
        area=("area_km2", "first"),
    )
    .reset_index()
)

print("Glacier-level rows:", glacier_stats.shape)

# -----------------------------
# CORRELATION ANALYSIS
# -----------------------------
corrs = []
for var in ["temp", "prec", "srad", "area"]:
    r, p = pearsonr(glacier_stats[var], glacier_stats["mean_melt"])
    corrs.append({
        "variable": var,
        "pearson_r": r,
        "p_value": p
    })

corr_df = pd.DataFrame(corrs)
corr_df.to_csv(
    os.path.join(OUT_DIR, "spatial_climate_correlation.csv"),
    index=False
)

print("\nSpatial correlation results:")
print(corr_df)

# -----------------------------
# MULTIPLE LINEAR REGRESSION
# mean_melt ~ temp + prec + srad + area
# -----------------------------
X = glacier_stats[["temp", "prec", "srad", "area"]].values
y = glacier_stats["mean_melt"].values

# Add intercept
X = np.column_stack([np.ones(len(X)), X])

coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
y_pred = X @ coef

# R²
ss_res = np.sum((y - y_pred) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2 = 1 - ss_res / ss_tot

regression = pd.DataFrame({
    "term": ["intercept", "temp", "prec", "srad", "area"],
    "coefficient": coef
})
regression["R_squared"] = r2

regression.to_csv(
    os.path.join(OUT_DIR, "spatial_climate_regression.csv"),
    index=False
)

print("\nRegression coefficients:")
print(regression)

print("\n✅ Spatial climate sensitivity analysis completed")
