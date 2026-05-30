from __future__ import annotations

import argparse
from pathlib import Path

from training.config import DATA_FILE, MODEL_ARTIFACT_DIR, RANDOM_STATE, VALID_SIZE


def add_training_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--data-path", type=Path, default=DATA_FILE, help="Path to movies.csv")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=MODEL_ARTIFACT_DIR,
        help="Directory for saved model artifacts",
    )
    parser.add_argument("--valid-size", type=float, default=VALID_SIZE, help="Validation split ratio")
    parser.add_argument("--random-state", type=int, default=RANDOM_STATE, help="Random seed")
    return parser


def print_summary(payload: dict) -> None:
    print(f"source rows: {payload['source_rows']}")
    print(f"train rows: {payload['train_rows']}")
    print(f"valid rows: {payload['valid_rows']}")
    print(f"feature count: {payload['feature_count']}")
    if "ensemble" in payload:
        weights = payload["ensemble"]["weights"]
        metrics = payload["ensemble"]["metrics"]
        print(f"ensemble weights: xgboost={weights['xgboost']:.2f}, lightgbm={weights['lightgbm']:.2f}")
        print(f"ensemble rmse_log: {metrics['rmse_log']:.4f}")
        print(f"ensemble mae_revenue: {metrics['mae_revenue']:.2f}")
    elif "xgboost" in payload:
        metrics = payload["xgboost"]["metrics"]
        print(f"xgboost rmse_log: {metrics['rmse_log']:.4f}")
    elif "lightgbm" in payload:
        metrics = payload["lightgbm"]["metrics"]
        print(f"lightgbm rmse_log: {metrics['rmse_log']:.4f}")
