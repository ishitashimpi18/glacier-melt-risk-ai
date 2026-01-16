"""
09_visualization.py
Generate plots and summary outputs for dashboard & evaluation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# PATHS
# -----------------------------
DATA_DIR = "data/processed"
OUT_DIR = "data/processed/visuals"

ML_FILE = os.path.join(DATA_DIR, "glacier_ml_dataset.csv")
FUTURE_FILE = os.path.join(DATA_DIR, "future_melt_projection.csv")
FLOOD_FILE = os.path.join(DATA_DIR, "flood_risk_index.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------
# LOAD DATA
# -----------------------------
ml = pd.read_csv(ML_FILE)
future = pd.read_csv(FUTURE_FILE)
flood = pd.read_csv(FLOOD_FILE)

print("ML data:", ml.shape)
print("Future data:", future.shape)
print("Flood data:", flood.shape)

# -----------------------------
# 1️⃣ HISTORICAL MELT TREND (2000–2024)
# -----------------------------
hist_trend = (
    ml.groupby("year")["mass_change"]
    .mean()
    .reset_index()
)

plt.figure()
plt.plot(hist_trend["year"], hist_trend["mass_change"])
plt.xlabel("Year")
plt.ylabel("Mean Mass Change")
plt.title("Historical Glacier Melt Trend (2000–2024)")
plt.grid(True)

plt.savefig(os.path.join(OUT_DIR, "historical_melt_trend.png"))
plt.close()

print("✅ Historical melt trend saved")

# -----------------------------
# 2️⃣ FUTURE MELT PROJECTION (2025–2040)
# -----------------------------
future_trend = (
    future.groupby("year")["predicted_melt"]
    .mean()
    .reset_index()
)

plt.figure()
plt.plot(future_trend["year"], future_trend["predicted_melt"], color="red")

plt.xlabel("Year")
plt.ylabel("Predicted Melt")
plt.title("Projected Glacier Melt (2025–2040)")
plt.grid(True)

# 🔴 ADD THIS PART HERE
plt.yticks(
    [-0.26, -0.255, -0.25, -0.245, -0.24],
    ["-0.26", "-0.255", "-0.25", "-0.245", "-0.24"]
)
plt.gca().invert_yaxis()
# 🔴 END HERE

plt.savefig(os.path.join(OUT_DIR, "future_melt_projection.png"))
plt.close()



# -----------------------------
# 3️⃣ FLOOD RISK DISTRIBUTION
# -----------------------------
plt.figure()
sns.countplot(
    data=flood,
    x="flood_risk_level",
    order=["Low Risk", "Moderate Risk", "High Risk"]
)
plt.title("Flood Risk Distribution (2000–2024)")
plt.xlabel("Flood Risk Level")
plt.ylabel("Number of Basin-Years")

plt.savefig(os.path.join(OUT_DIR, "flood_risk_distribution.png"))
plt.close()

print("✅ Flood risk distribution saved")

# -----------------------------
# 4️⃣ SUMMARY CSVs FOR DASHBOARD
# -----------------------------
hist_trend.to_csv(
    os.path.join(OUT_DIR, "historical_melt_summary.csv"),
    index=False
)

future_trend.to_csv(
    os.path.join(OUT_DIR, "future_melt_summary.csv"),
    index=False
)

flood.to_csv(
    os.path.join(OUT_DIR, "flood_risk_summary.csv"),
    index=False
)

print("✅ Dashboard summary CSVs saved")

print("\n🎉 Visualization pipeline completed successfully")
