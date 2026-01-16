from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

# -----------------------------
# LOAD MODEL & SCALER
# -----------------------------
MODEL_PATH = "../model/risk_model.pkl"
SCALER_PATH = "../model/scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(
    title="NEO Risk Prediction API",
    description="Predicts asteroid collision risk using ML",
    version="1.0"
)

# -----------------------------
# INPUT SCHEMA
# -----------------------------
class AsteroidInput(BaseModel):
    distance_km: float
    velocity_kms: float
    diameter_m: float
    trajectory_angle_deg: float

# -----------------------------
# ROOT ENDPOINT
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "NEO Risk Prediction API is running",
        "status": "OK"
    }

# -----------------------------
# PREDICTION ENDPOINT
# -----------------------------
@app.post("/predict")
def predict_risk(data: AsteroidInput):
    # Convert input to numpy array
    input_array = np.array([[
        data.distance_km,
        data.velocity_kms,
        data.diameter_m,
        data.trajectory_angle_deg
    ]])

    # Scale input
    input_scaled = scaler.transform(input_array)

    # Predict risk level
    risk_prediction = model.predict(input_scaled)[0]

    # Predict probability
    risk_probabilities = model.predict_proba(input_scaled)[0]
    max_probability = float(np.max(risk_probabilities))

    return {
        "risk_level": risk_prediction,
        "impact_probability": round(max_probability, 3)
    }
