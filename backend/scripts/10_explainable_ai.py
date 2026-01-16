"""
10_explainable_ai.py
Explainable AI analysis for glacier melt drivers
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

FEATURE_IMPORTANCE_FILE = os.path.join(OUT_DIR, "feature_importance.csv")
PARTIAL_EFFECT_FILE = os.path.join(OUT_DIR, "partial_effects.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)
print("Loaded ML dataset:", df.shape)

# -----------------------------
# FEATURES & TARGET
# -----------------------------
features = ["temp_mean", "prec_mean", "srad_mean", "area_km2"]
target = "mass_change"

X = df[features]
y = df[target]

# -----------------------------
# TRAIN MODEL
# -----------------------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)
print("✅ Model trained for explainability")

# -----------------------------
# 1️⃣ FEATURE IMPORTANCE
# -----------------------------
importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

importance.to_csv(FEATURE_IMPORTANCE_FILE, index=False)

print("\nFeature importance:")
print(importance)

# -----------------------------
# 2️⃣ PARTIAL EFFECT (SIMPLE SHAP-LIKE)
# -----------------------------
effects = []

for feature in features:
    x_vals = np.linspace(
        X[feature].quantile(0.05),
        X[feature].quantile(0.95),
        20
    )

    base = X.mean().values.reshape(1, -1)

    for val in x_vals:
        temp = base.copy()
        temp[0, features.index(feature)] = val
        pred = model.predict(temp)[0]

        effects.append({
            "feature": feature,
            "feature_value": val,
            "predicted_melt": pred
        })

effects_df = pd.DataFrame(effects)
effects_df.to_csv(PARTIAL_EFFECT_FILE, index=False)

print("\n✅ Partial effects saved")

print("\n🎯 Explainable AI analysis completed")
