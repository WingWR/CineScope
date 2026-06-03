from __future__ import annotations

import numpy as np

from training.evaluation.metrics import regression_metrics


def weighted_predictions(
    xgboost_pred_log: np.ndarray,
    lightgbm_pred_log: np.ndarray,
    xgboost_weight: float,
) -> np.ndarray:
    weight = float(np.clip(xgboost_weight, 0.0, 1.0))
    return weight * xgboost_pred_log + (1.0 - weight) * lightgbm_pred_log


def search_best_weight(
    y_valid_log: np.ndarray,
    xgboost_pred_log: np.ndarray,
    lightgbm_pred_log: np.ndarray,
    step: float = 0.02,
) -> tuple[dict[str, float], dict[str, float]]:
    candidates = np.arange(0.0, 1.0 + step / 2, step)
    best_weight = 0.5
    best_metrics: dict[str, float] | None = None

    for weight in candidates:
        prediction = weighted_predictions(xgboost_pred_log, lightgbm_pred_log, weight)
        metrics = regression_metrics(y_valid_log, prediction)
        if best_metrics is None or metrics["rmse_log"] < best_metrics["rmse_log"]:
            best_weight = float(weight)
            best_metrics = metrics

    assert best_metrics is not None
    return {"xgboost": best_weight, "lightgbm": 1.0 - best_weight}, best_metrics
