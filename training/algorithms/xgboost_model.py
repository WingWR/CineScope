from __future__ import annotations

import pandas as pd

from training.config import XGBOOST_PARAMS


def train_xgboost_regressor(
    x_train: pd.DataFrame,
    y_train,
    x_valid: pd.DataFrame,
    y_valid,
    params: dict | None = None,
    num_boost_round: int = 900,
    early_stopping_rounds: int = 60,
):
    try:
        import xgboost as xgb
    except ImportError as exc:
        raise ImportError(
            "xgboost is required. Install training dependencies with: "
            "python -m pip install -r requirements.txt"
        ) from exc

    train_matrix = xgb.DMatrix(x_train, label=y_train, feature_names=list(x_train.columns))
    valid_matrix = xgb.DMatrix(x_valid, label=y_valid, feature_names=list(x_valid.columns))
    model_params = dict(XGBOOST_PARAMS)
    if params:
        model_params.update(params)

    return xgb.train(
        model_params,
        train_matrix,
        num_boost_round=num_boost_round,
        evals=[(train_matrix, "train"), (valid_matrix, "valid")],
        early_stopping_rounds=early_stopping_rounds,
        verbose_eval=False,
    )


def predict_xgboost(model, features: pd.DataFrame):
    import xgboost as xgb

    matrix = xgb.DMatrix(features, feature_names=list(features.columns))
    return model.predict(matrix)
