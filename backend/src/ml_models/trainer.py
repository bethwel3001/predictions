import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from datetime import timedelta
from .feature_engineer import FeatureEngineer

MODEL_PATH = "backend/src/ml_models/air_quality_model.pkl"

def train_model(data: pd.DataFrame):
    fe = FeatureEngineer()
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = fe.add_features(data)

    # Sort chronologically
    data = data.sort_values("timestamp")

    # Train/test split (30 days train, 7 days test)
    cutoff = data["timestamp"].max() - timedelta(days=7)
    train = data[data["timestamp"] <= cutoff]
    test = data[data["timestamp"] > cutoff]

    X_train = train[["hour", "day", "season"]]
    y_train = train["pm25"]
    X_test = test[["hour", "day", "season"]]
    y_test = test["pm25"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    joblib.dump(model, MODEL_PATH)

    return {"mse": mse, "r2": r2}
    