import numpy as np
import pandas as pd
import joblib
from datetime import timedelta
from .feature_engineer import FeatureEngineer
from .model_loader import load_model

def forecast(df: pd.DataFrame, hours=24):
    model = load_model()
    fe = FeatureEngineer()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    last_time = df["timestamp"].max()
    future_timestamps = [last_time + timedelta(hours=i) for i in range(1, hours + 1)]
    forecast_df = pd.DataFrame({"timestamp": future_timestamps})
    forecast_df = fe.add_features(forecast_df)

    X = forecast_df[["hour", "day", "season"]]
    preds = model.predict(X)

    # Confidence intervals (approx ±10%)
    lower = preds * 0.9
    upper = preds * 1.1

    return pd.DataFrame({
        "timestamp": future_timestamps,
        "pm25_pred": preds,
        "lower": lower,
        "upper": upper
    })