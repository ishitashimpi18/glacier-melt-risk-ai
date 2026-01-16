"""
07_trend_analysis.py
Long-term glacier runoff trend analysis (2000–2024)
"""

import pandas as pd
import numpy as np
import os

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = "data/processed/basin_runoff_timeseries.csv"
OUT_DIR = "data/processed"
OUT_FILE = os.path.join(OUT_DIR, "glacier_runoff_trend.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)
print("Loaded basin runoff data:", df.shape)

# -----------------------------
# LINEAR TREND (runoff vs year)
# -----------------------------
years = df["year"].values
runoff = df["basin_runoff_mm"].values

# Linear regression (1st order poly)
slope, intercept = np.polyfit(years, runoff, 1)

trend_type = "Increasing" if slope > 0 else "Decreasing"

# -----------------------------
# SAVE RESULT
# -----------------------------
trend_df = pd.DataFrame([{
    "basin": df["basin"].iloc[0],
    "start_year": years.min(),
    "end_year": years.max(),
    "runoff_trend_mm_per_year": slope,
    "trend_type": trend_type
}])

os.makedirs(OUT_DIR, exist_ok=True)
trend_df.to_csv(OUT_FILE, index=False)

print("✅ Glacier runoff trend analysis completed")
print(trend_df)
