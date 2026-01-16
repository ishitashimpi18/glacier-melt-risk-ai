"""
08_future_melt_projection.py
Project future glacier melt using ML regression
"""

import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = "data/processed/glacier_ml_dataset.csv"
OUT_DIR = "data/processed"
OUT_FILE = os.path.join(OUT_DIR, "future_melt_projection.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)
print("Loaded ML dataset:", df.shape)

# -----------------------------
# TRAINING DATA (2000–2024)
# -----------------------------
train = df[(df["year"] >= 2000) & (df["year"] <= 2024)].copy()

X = train[["area_km2", "temp_mean", "prec_mean", "srad_mean"]]
y = train["mass_change"]

# -----------------------------
# TRAIN MODEL
# -----------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)
model.fit(X, y)

print("✅ Model trained")

# -----------------------------
# FUTURE SCENARIOS (2025–2040)
# -----------------------------
future_years = list(range(2025, 2041))

# Baseline glacier-level climate (latest observed)
baseline = (
    df.groupby("glacier_id")
    .agg(
        area_km2=("area_km2", "first"),
        temp_mean=("temp_mean", "mean"),
        prec_mean=("prec_mean", "mean"),
        srad_mean=("srad_mean", "mean"),
    )
    .reset_index()
)

projections = []

for year in future_years:
    temp_inc = 0.04 * (year - 2024)   # +0.04°C per year
    prec_inc = 0.002 * (year - 2024)  # +0.2% per year
    srad_inc = 0.001 * (year - 2024)

    future = baseline.copy()
    future["year"] = year
    future["temp_mean"] += temp_inc
    future["prec_mean"] *= (1 + prec_inc)
    future["srad_mean"] *= (1 + srad_inc)

    X_future = future[["area_km2", "temp_mean", "prec_mean", "srad_mean"]]
    future["predicted_melt"] = model.predict(X_future)

    projections.append(future)

# -----------------------------
# COMBINE & SAVE
# -----------------------------
future_df = pd.concat(projections, ignore_index=True)

os.makedirs(OUT_DIR, exist_ok=True)
future_df.to_csv(OUT_FILE, index=False)

print("✅ Future melt projection created")
print("Years:", future_df["year"].min(), "-", future_df["year"].max())
print("Rows:", future_df.shape)
print(future_df.head())
