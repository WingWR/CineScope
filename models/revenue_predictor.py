from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.revenue_features import load_revenue_feature_schema, transform_revenue_features


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts" / "revenue_prediction"
XGBOOST_MODEL_FILE = ARTIFACT_DIR / "xgboost_revenue.json"
LIGHTGBM_MODEL_FILE = ARTIFACT_DIR / "lightgbm_revenue.txt"
FEATURE_SCHEMA_FILE = ARTIFACT_DIR / "feature_schema.json"
ENSEMBLE_CONFIG_FILE = ARTIFACT_DIR / "ensemble_config.json"


class RevenuePredictor:
    def __init__(self, artifact_dir: str | Path = ARTIFACT_DIR) -> None:
        self.artifact_dir = Path(artifact_dir)
        self.schema = load_revenue_feature_schema(self.artifact_dir / "feature_schema.json")
        self.weights = self._load_weights(self.artifact_dir / "ensemble_config.json")
        self.xgboost_model = self._load_xgboost_model(self.artifact_dir / "xgboost_revenue.json")
        self.lightgbm_model = self._load_lightgbm_model(self.artifact_dir / "lightgbm_revenue.txt")

    def predict_frame(self, movies: pd.DataFrame) -> pd.DataFrame:
        features = transform_revenue_features(movies, self.schema)
        xgb_log = self._predict_xgboost(features)
        lgb_log = self._predict_lightgbm(features)
        ensemble_log = (
            self.weights["xgboost"] * xgb_log
            + self.weights["lightgbm"] * lgb_log
        )
        predictions = np.expm1(np.clip(ensemble_log, 0, None))

        result = movies.copy()
        result["predicted_revenue"] = predictions
        result["predicted_log_revenue"] = ensemble_log
        result["xgboost_predicted_revenue"] = np.expm1(np.clip(xgb_log, 0, None))
        result["lightgbm_predicted_revenue"] = np.expm1(np.clip(lgb_log, 0, None))
        return result

    def _predict_xgboost(self, features: pd.DataFrame) -> np.ndarray:
        import xgboost as xgb

        matrix = xgb.DMatrix(features, feature_names=list(features.columns))
        return self.xgboost_model.predict(matrix)

    def _predict_lightgbm(self, features: pd.DataFrame) -> np.ndarray:
        return self.lightgbm_model.predict(features)

    @staticmethod
    def _load_xgboost_model(path: Path):
        import xgboost as xgb

        model = xgb.Booster()
        model.load_model(path)
        return model

    @staticmethod
    def _load_lightgbm_model(path: Path):
        import lightgbm as lgb

        return lgb.Booster(model_file=str(path))

    @staticmethod
    def _load_weights(path: Path) -> dict[str, float]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        weights = payload.get("weights", {"xgboost": 0.5, "lightgbm": 0.5})
        total = float(weights.get("xgboost", 0.0) + weights.get("lightgbm", 0.0))
        if total <= 0:
            return {"xgboost": 0.5, "lightgbm": 0.5}
        return {
            "xgboost": float(weights.get("xgboost", 0.0)) / total,
            "lightgbm": float(weights.get("lightgbm", 0.0)) / total,
        }


def load_predictor(artifact_dir: str | Path = ARTIFACT_DIR) -> RevenuePredictor:
    return RevenuePredictor(artifact_dir)
