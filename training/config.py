from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "data" / "final" / "movies.csv"
MODEL_ARTIFACT_DIR = ROOT_DIR / "models" / "artifacts" / "revenue_prediction"

FEATURE_SCHEMA_FILE = MODEL_ARTIFACT_DIR / "feature_schema.json"
XGBOOST_MODEL_FILE = MODEL_ARTIFACT_DIR / "xgboost_revenue.json"
LIGHTGBM_MODEL_FILE = MODEL_ARTIFACT_DIR / "lightgbm_revenue.txt"
ENSEMBLE_CONFIG_FILE = MODEL_ARTIFACT_DIR / "ensemble_config.json"
METRICS_FILE = MODEL_ARTIFACT_DIR / "metrics.json"

RANDOM_STATE = 42
VALID_SIZE = 0.2

XGBOOST_PARAMS = {
    "objective": "reg:squarederror",
    "eval_metric": "rmse",
    "eta": 0.035,
    "max_depth": 4,
    "min_child_weight": 2.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "lambda": 1.0,
    "alpha": 0.05,
    "tree_method": "hist",
    "seed": RANDOM_STATE,
}

LIGHTGBM_PARAMS = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.035,
    "num_leaves": 31,
    "min_data_in_leaf": 12,
    "feature_fraction": 0.85,
    "bagging_fraction": 0.85,
    "bagging_freq": 1,
    "lambda_l1": 0.05,
    "lambda_l2": 1.0,
    "verbosity": -1,
    "seed": RANDOM_STATE,
    "feature_fraction_seed": RANDOM_STATE,
    "bagging_seed": RANDOM_STATE,
    "force_col_wise": True,
}
