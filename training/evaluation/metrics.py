from __future__ import annotations

import numpy as np


def regression_metrics(y_true_log: np.ndarray, y_pred_log: np.ndarray) -> dict[str, float]:
    y_pred_log = np.asarray(y_pred_log, dtype=float)
    y_true_log = np.asarray(y_true_log, dtype=float)
    y_pred_log_clipped = np.clip(y_pred_log, 0, None)

    y_true = np.expm1(y_true_log)
    y_pred = np.expm1(y_pred_log_clipped)
    residual_log = y_true_log - y_pred_log
    residual = y_true - y_pred

    return {
        "rmse_log": _rmse(residual_log),
        "mae_log": float(np.mean(np.abs(residual_log))),
        "r2_log": _r2(y_true_log, y_pred_log),
        "rmse_revenue": _rmse(residual),
        "mae_revenue": float(np.mean(np.abs(residual))),
        "mape_revenue": _mape(y_true, y_pred),
    }


def _rmse(residual: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(residual))))


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denominator = float(np.sum(np.square(y_true - np.mean(y_true))))
    if denominator == 0:
        return 0.0
    numerator = float(np.sum(np.square(y_true - y_pred)))
    return 1.0 - numerator / denominator


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = y_true > 0
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))
