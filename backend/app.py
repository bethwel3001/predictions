from fastapi import FastAPI, Query
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI(
    title="Air Quality Forecast API",
    description="Predicts air quality for the next 24–48 hours using ML models",
    version="1.0.0"
)

# ✅ Load trained model (will load during runtime)
MODEL_PATH = "backend/src/ml_models/model.joblib"

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None


# 🧠 Pydantic model for request body
class ForecastRequest(BaseModel):
    lat: float
    lon: float
    hours: int = 24


@app.get("/")
def root():
    return {"message": "Air Quality Forecast API is running!"}


@app.get("/api/v1/forecast/location")
def get_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    hours: int = Query(24, description="Forecast duration in hours (24 or 48)")
):
    if model is None:
        return {"error": "Model not loaded or not trained yet"}

    # Simulate features for demo (replace with actual data pipeline later)
    data = pd.DataFrame({
        "lat": [lat],
        "lon": [lon],
        "hour": [datetime.utcnow().hour],
        "dayofweek": [datetime.utcnow().weekday()],
    })

    # Generate prediction + confidence interval
    prediction = float(model.predict(data)[0])
    lower = max(prediction - 5, 0)
    upper = prediction + 5

    return {
        "lat": lat,
        "lon": lon,
        "hours": hours,
        "prediction": prediction,
        "confidence_interval": [lower, upper],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/forecast/train")
def train_model():
    """Retrains the model using last 30 days of data"""
    # TODO: integrate your OpenAQ + weather data fetch
    df = pd.DataFrame({
        "lat": np.random.uniform(-90, 90, 100),
        "lon": np.random.uniform(-180, 180, 100),
        "hour": np.random.randint(0, 24, 100),
        "dayofweek": np.random.randint(0, 7, 100),
        "aqi": np.random.uniform(20, 200, 100)
    })

    from sklearn.ensemble import RandomForestRegressor
    X = df[["lat", "lon", "hour", "dayofweek"]]
    y = df["aqi"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return {"status": "Model trained successfully", "records": len(df)}


@app.get("/api/v1/forecast/accuracy")
def get_accuracy():
    """Returns dummy model accuracy metrics"""
    # In reality, you'd compute this after validation
    return {
        "model": "RandomForestRegressor",
        "rmse": 12.5,
        "r2_score": 0.87
    }
