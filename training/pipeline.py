from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from training.config import (
    DATA_FILE,
    ENSEMBLE_CONFIG_FILE,
    FEATURE_SCHEMA_FILE,
    LIGHTGBM_MODEL_FILE,
    METRICS_FILE,
    MODEL_ARTIFACT_DIR,
    RANDOM_STATE,
    VALID_SIZE,
    XGBOOST_MODEL_FILE,
)
from training.data.features import (
    build_feature_matrix,
    filter_revenue_training_rows,
    save_revenue_feature_schema,
)
from training.data.loader import load_revenue_training_source
from training.data.split import train_valid_split
from training.evaluation.metrics import regression_metrics


@dataclass
class PreparedRevenueData:
    x_train: Any
    y_train: Any
    x_valid: Any
    y_valid: Any
    schema: Any
    train_count: int
    valid_count: int
    source_count: int


def prepare_revenue_data(
    data_path: str | Path = DATA_FILE,
    valid_size: float = VALID_SIZE,
    random_state: int = RANDOM_STATE,
) -> PreparedRevenueData:
    source = load_revenue_training_source(data_path)
    filtered = filter_revenue_training_rows(source)
    train_df, valid_df = train_valid_split(filtered, valid_size, random_state)
    x_train, y_train, x_valid, y_valid, schema = build_feature_matrix(train_df, valid_df)
    return PreparedRevenueData(
        x_train=x_train,
        y_train=y_train,
        x_valid=x_valid,
        y_valid=y_valid,
        schema=schema,
        train_count=len(train_df),
        valid_count=len(valid_df),
        source_count=len(source),
    )


def run_xgboost_training(
    data_path: str | Path = DATA_FILE,
    output_dir: str | Path = MODEL_ARTIFACT_DIR,
    valid_size: float = VALID_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    from training.algorithms.xgboost_model import predict_xgboost, train_xgboost_regressor

    paths = _artifact_paths(output_dir)
    prepared = prepare_revenue_data(data_path, valid_size, random_state)
    model = train_xgboost_regressor(
        prepared.x_train,
        prepared.y_train,
        prepared.x_valid,
        prepared.y_valid,
    )
    predictions = predict_xgboost(model, prepared.x_valid)
    metrics = regression_metrics(prepared.y_valid, predictions)

    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    model.save_model(paths["xgboost_model"])
    save_revenue_feature_schema(prepared.schema, paths["feature_schema"])

    payload = _metadata(prepared, data_path, valid_size, random_state)
    payload["xgboost"] = {"metrics": metrics}
    _write_json(paths["metrics"].with_name("metrics_xgboost.json"), payload)
    return payload


def run_lightgbm_training(
    data_path: str | Path = DATA_FILE,
    output_dir: str | Path = MODEL_ARTIFACT_DIR,
    valid_size: float = VALID_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    from training.algorithms.lightgbm_model import predict_lightgbm, train_lightgbm_regressor

    paths = _artifact_paths(output_dir)
    prepared = prepare_revenue_data(data_path, valid_size, random_state)
    model = train_lightgbm_regressor(
        prepared.x_train,
        prepared.y_train,
        prepared.x_valid,
        prepared.y_valid,
    )
    predictions = predict_lightgbm(model, prepared.x_valid)
    metrics = regression_metrics(prepared.y_valid, predictions)

    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    model.save_model(str(paths["lightgbm_model"]))
    save_revenue_feature_schema(prepared.schema, paths["feature_schema"])

    payload = _metadata(prepared, data_path, valid_size, random_state)
    payload["lightgbm"] = {"metrics": metrics}
    _write_json(paths["metrics"].with_name("metrics_lightgbm.json"), payload)
    return payload


def run_ensemble_training(
    data_path: str | Path = DATA_FILE,
    output_dir: str | Path = MODEL_ARTIFACT_DIR,
    valid_size: float = VALID_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    from training.algorithms.ensemble import search_best_weight, weighted_predictions
    from training.algorithms.lightgbm_model import predict_lightgbm, train_lightgbm_regressor
    from training.algorithms.xgboost_model import predict_xgboost, train_xgboost_regressor

    paths = _artifact_paths(output_dir)
    prepared = prepare_revenue_data(data_path, valid_size, random_state)

    xgboost_model = train_xgboost_regressor(
        prepared.x_train,
        prepared.y_train,
        prepared.x_valid,
        prepared.y_valid,
    )
    lightgbm_model = train_lightgbm_regressor(
        prepared.x_train,
        prepared.y_train,
        prepared.x_valid,
        prepared.y_valid,
    )

    xgb_pred = predict_xgboost(xgboost_model, prepared.x_valid)
    lgb_pred = predict_lightgbm(lightgbm_model, prepared.x_valid)
    weights, ensemble_metrics = search_best_weight(prepared.y_valid, xgb_pred, lgb_pred)
    ensemble_pred = weighted_predictions(xgb_pred, lgb_pred, weights["xgboost"])

    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    xgboost_model.save_model(paths["xgboost_model"])
    lightgbm_model.save_model(str(paths["lightgbm_model"]))
    save_revenue_feature_schema(prepared.schema, paths["feature_schema"])

    ensemble_config = {
        "weights": weights,
        "selection_metric": "rmse_log",
        "target_transform": "log1p",
        "created_at": _utc_now(),
    }
    _write_json(paths["ensemble_config"], ensemble_config)

    payload = _metadata(prepared, data_path, valid_size, random_state)
    payload["xgboost"] = {"metrics": regression_metrics(prepared.y_valid, xgb_pred)}
    payload["lightgbm"] = {"metrics": regression_metrics(prepared.y_valid, lgb_pred)}
    payload["ensemble"] = {
        "weights": weights,
        "metrics": regression_metrics(prepared.y_valid, ensemble_pred),
    }
    payload["ensemble"]["metrics_selected_during_search"] = ensemble_metrics
    _write_json(paths["metrics"], payload)
    return payload


def _artifact_paths(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    if output == MODEL_ARTIFACT_DIR:
        return {
            "output_dir": MODEL_ARTIFACT_DIR,
            "feature_schema": FEATURE_SCHEMA_FILE,
            "xgboost_model": XGBOOST_MODEL_FILE,
            "lightgbm_model": LIGHTGBM_MODEL_FILE,
            "ensemble_config": ENSEMBLE_CONFIG_FILE,
            "metrics": METRICS_FILE,
        }
    return {
        "output_dir": output,
        "feature_schema": output / "feature_schema.json",
        "xgboost_model": output / "xgboost_revenue.json",
        "lightgbm_model": output / "lightgbm_revenue.txt",
        "ensemble_config": output / "ensemble_config.json",
        "metrics": output / "metrics.json",
    }


def _metadata(
    prepared: PreparedRevenueData,
    data_path: str | Path,
    valid_size: float,
    random_state: int,
) -> dict[str, Any]:
    return {
        "created_at": _utc_now(),
        "data_path": str(Path(data_path).resolve()),
        "source_rows": prepared.source_count,
        "train_rows": prepared.train_count,
        "valid_rows": prepared.valid_count,
        "feature_count": len(prepared.schema.feature_columns),
        "valid_size": valid_size,
        "random_state": random_state,
        "target": "log1p(revenue)",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
