import joblib
import os

MODEL_PATH = "backend/src/ml_models/air_quality_model.pkl"

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Please train it first.")
    return joblib.load(MODEL_PATH)
    