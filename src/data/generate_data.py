import numpy as np
import pandas as pd
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_SAMPLES = 10000
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "asteroid_raw.csv"

np.random.seed(42)

# -----------------------------
# DATA GENERATION
# -----------------------------

# Distance from Earth (in km)
# Range: 50,000 km to 10,000,000 km
distance_km = np.random.uniform(5e4, 1e7, NUM_SAMPLES)

# Velocity (km/s)
# Typical asteroid speeds: 5 km/s to 40 km/s
velocity_kms = np.random.uniform(5, 40, NUM_SAMPLES)

# Diameter (meters)
# Small meteoroids to large asteroids
diameter_m = np.random.uniform(5, 1000, NUM_SAMPLES)

# Trajectory angle (degrees)
# 0° = direct hit, 90° = tangential pass
trajectory_angle_deg = np.random.uniform(0, 90, NUM_SAMPLES)

# -----------------------------
# RISK SCORING LOGIC
# -----------------------------

# Normalize values for scoring
distance_score = 1 - (distance_km / distance_km.max())
velocity_score = velocity_kms / velocity_kms.max()
size_score = diameter_m / diameter_m.max()
angle_score = 1 - (trajectory_angle_deg / 90)

# Weighted risk score
risk_score = (
    0.4 * distance_score +
    0.3 * velocity_score +
    0.2 * size_score +
    0.1 * angle_score
)

# -----------------------------
# RISK LABELS
# -----------------------------

risk_level = []

for score in risk_score:
    if score < 0.35:
        risk_level.append("Low")
    elif score < 0.65:
        risk_level.append("Medium")
    else:
        risk_level.append("High")

# -----------------------------
# IMPACT PROBABILITY
# -----------------------------

impact_probability = np.clip(
    risk_score + np.random.normal(0, 0.05, NUM_SAMPLES),
    0,
    1
)

# -----------------------------
# CREATE DATAFRAME
# -----------------------------

df = pd.DataFrame({
    "distance_km": distance_km,
    "velocity_kms": velocity_kms,
    "diameter_m": diameter_m,
    "trajectory_angle_deg": trajectory_angle_deg,
    "risk_score": risk_score,
    "risk_level": risk_level,
    "impact_probability": impact_probability
})

# -----------------------------
# SAVE DATA
# -----------------------------

df.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset generated successfully!")
print(f"Saved to: {OUTPUT_PATH}")
print(df.head())
