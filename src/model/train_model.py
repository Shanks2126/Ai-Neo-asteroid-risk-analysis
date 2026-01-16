import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# -----------------------------
# CONFIGURATION
# -----------------------------
DATA_PATH = "../../data/raw/asteroid_raw.csv"
MODEL_OUTPUT_PATH = "risk_model.pkl"
SCALER_OUTPUT_PATH = "scaler.pkl"

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(DATA_PATH)

# Features and labels
X = df[
    [
        "distance_km",
        "velocity_kms",
        "diameter_m",
        "trajectory_angle_deg",
    ]
]

y = df["risk_level"]

# -----------------------------
# TRAIN / TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# FEATURE SCALING
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# MODEL TRAINING
# -----------------------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train_scaled, y_train)

# -----------------------------
# MODEL EVALUATION
# -----------------------------
y_pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Training Completed")
print("------------------------")
print(f"Accuracy: {accuracy:.4f}\n")

print("Classification Report:")
print(classification_report(y_test, y_pred))

# -----------------------------
# SAVE MODEL & SCALER
# -----------------------------
joblib.dump(model, MODEL_OUTPUT_PATH)
joblib.dump(scaler, SCALER_OUTPUT_PATH)

print("\nModel saved as:", MODEL_OUTPUT_PATH)
print("Scaler saved as:", SCALER_OUTPUT_PATH)
