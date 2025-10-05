# backend/src/ml_models/feature_engineer.py
import pandas as pd
from sklearn.preprocessing import StandardScaler

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()

    def add_features(self, df: pd.DataFrame):
        df["hour"] = df["timestamp"].dt.hour
        df["day"] = df["timestamp"].dt.dayofyear
        df["month"] = df["timestamp"].dt.month
        df["season"] = ((df["month"] % 12 + 3) // 3).astype(int)
        return df

    def normalize(self, df: pd.DataFrame, fit=False):
        if fit:
            df[df.columns] = self.scaler.fit_transform(df)
        else:
            df[df.columns] = self.scaler.transform(df)
        return df
     
        