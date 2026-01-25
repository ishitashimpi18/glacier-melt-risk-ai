from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import pandas as pd

# ===============================
# PATH CONFIG
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
VIS_DIR = os.path.join(DATA_DIR, "visuals")

print("🚀 Starting Flask app...")
print("TEMPLATE_DIR:", TEMPLATE_DIR)
print("STATIC_DIR:", STATIC_DIR)

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# ===============================
# PAGE ROUTES
# ===============================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/glacier-explorer")
def glacier_explorer():
    return render_template("glacier_explorer.html")

@app.route("/melt-trends")
def melt_trends():
    return render_template("melt_trends.html")

@app.route("/explainable-ai")
def explainable_ai():
    return render_template("explainable_ai.html")

@app.route("/vulnerability")
def vulnerability():
    return render_template("vulnerability.html")

@app.route("/water-impact")
def water_impact():
    return render_template("water_impact.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/flood-risk")
def flood_risk():
    return render_template("flood_risk.html")

# ===============================
# GLACIER API (SINGLE SOURCE OF TRUTH)
# ===============================
@app.route("/api/glaciers")
def api_glaciers():
    FILE = os.path.join(
        BASE_DIR, "data", "processed", "glacier_explorer_merged.csv"
    )

    df = pd.read_csv(FILE)

    # Drop invalid geometry
    df = df.dropna(subset=["lat", "lon"])

    # 🚨 FORCE JSON-SAFE VALUES (THIS IS THE KEY FIX)
    df = df.replace({pd.NA: None, float("nan"): None})

    print(f"✅ Serving glaciers: {len(df)}")

    return jsonify(df.to_dict(orient="records"))

# ===============================
# OTHER DATA APIs (SAFE)
# ===============================
@app.route("/api/historical_melt")
def api_historical_melt():
    try:
        df = pd.read_csv(os.path.join(VIS_DIR, "historical_melt_summary.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])

@app.route("/api/future_melt")
def api_future_melt():
    try:
        df = pd.read_csv(os.path.join(VIS_DIR, "future_melt_summary.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])

@app.route("/api/flood_risk")
def api_flood_risk():
    try:
        df = pd.read_csv(os.path.join(VIS_DIR, "flood_risk_summary.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])

@app.route("/api/feature_importance")
def api_feature_importance():
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "feature_importance.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])

@app.route("/api/basin_runoff")
def api_basin_runoff():
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "basin_runoff_timeseries.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])
@app.route("/api/partial_effects")
def api_partial_effects():
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "partial_effects.csv"))
        return jsonify(df.to_dict(orient="records"))
    except:
        return jsonify([])

# ===============================
# RUN
# ===============================
# ===============================
# RUN (Render / Production Safe)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
