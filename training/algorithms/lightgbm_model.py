from __future__ import annotations

import pandas as pd

from training.config import LIGHTGBM_PARAMS


def train_lightgbm_regressor(
    x_train: pd.DataFrame,
    y_train,
    x_valid: pd.DataFrame,
    y_valid,
    params: dict | None = None,
    num_boost_round: int = 900,
    early_stopping_rounds: int = 60,
):
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise ImportError(
            "lightgbm is required. Install training dependencies with: "
            "python -m pip install -r requirements.txt"
        ) from exc

    model_params = dict(LIGHTGBM_PARAMS)
    if params:
        model_params.update(params)

    train_set = lgb.Dataset(
        x_train,
        label=y_train,
        feature_name=list(x_train.columns),
        free_raw_data=False,
    )
    valid_set = lgb.Dataset(
        x_valid,
        label=y_valid,
        feature_name=list(x_valid.columns),
        reference=train_set,
        free_raw_data=False,
    )

    return lgb.train(
        model_params,
        train_set,
        num_boost_round=num_boost_round,
        valid_sets=[train_set, valid_set],
        valid_names=["train", "valid"],
        callbacks=[
            lgb.early_stopping(early_stopping_rounds, verbose=False),
            lgb.log_evaluation(period=0),
        ],
    )


def predict_lightgbm(model, features: pd.DataFrame):
    return model.predict(features)
