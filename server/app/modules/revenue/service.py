from __future__ import annotations

import json
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException

from ...core.paths import MOVIES_FILE, MODELS_DIR
from ...shared.csv_loader import load_csv
from .schemas import (
    EnsembleWeights,
    FeatureSchemaItem,
    FeatureSchemaResponse,
    ModelMetrics,
    RevenuePredictionRequest,
    RevenuePredictionResponse,
)

NUMERIC_FIELD_META: list[dict[str, Any]] = [
    {"name": "budget", "label": "Budget (USD)", "description": "Production budget in US dollars", "defaultValue": 14_000_000},
    {"name": "movie_year", "label": "Release Year", "description": "Year the movie was released", "defaultValue": 2001},
    {"name": "runtime_minutes", "label": "Runtime (minutes)", "description": "Movie duration in minutes", "defaultValue": 105},
    {"name": "tmdb_popularity", "label": "TMDb Popularity", "description": "Popularity score from TMDb (0–100+)", "defaultValue": 2.73},
    {"name": "rating_mean", "label": "Avg Rating (0–5)", "description": "Mean user rating on MovieLens", "defaultValue": 3.33},
    {"name": "rating_median", "label": "Median Rating", "description": "Median user rating on MovieLens", "defaultValue": 3.5},
    {"name": "rating_count", "label": "Rating Count", "description": "Number of ratings received", "defaultValue": 5},
    {"name": "tag_count", "label": "Tag Count", "description": "Number of user tags assigned", "defaultValue": 0},
]


def _format_money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.0f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _fuzzy_match(query: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    query_lower = query.strip().lower()
    if not query_lower:
        return None

    best: dict[str, Any] | None = None
    best_score = 0.0

    for record in candidates:
        title = str(record.get("title_clean", record.get("title", ""))).strip()
        if not title:
            continue
        title_lower = title.lower()

        if title_lower == query_lower:
            return record

        score = SequenceMatcher(None, query_lower, title_lower).ratio()

        # Substring bonus — only when the shorter side is at least 3 chars
        if len(query_lower) >= 3 and query_lower in title_lower:
            score = max(score, 0.85)
        if len(title_lower) >= 3 and title_lower in query_lower:
            score = max(score, 0.80)

        # Word-overlap bonus: reward shared words of length >= 3
        query_words = {w for w in query_lower.split() if len(w) >= 3}
        title_words = {w for w in title_lower.split() if len(w) >= 3}
        common = query_words & title_words
        if common:
            word_score = len(common) / max(1, len(query_words))
            score = max(score, 0.55 + 0.25 * word_score)

        if score > best_score:
            best_score = score
            best = record

    if best_score >= 0.55:
        return best
    return None


class RevenueService:
    def __init__(self) -> None:
        self._predictor = None

    @property
    def predictor(self):
        if self._predictor is None:
            project_root = MODELS_DIR.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from models.revenue_predictor import RevenuePredictor

            self._predictor = RevenuePredictor()
        return self._predictor

    # ── schema ──────────────────────────────────────────────

    def get_schema(self) -> FeatureSchemaResponse:
        schema = self.predictor.schema
        numeric_fields = [
            FeatureSchemaItem(
                name=meta["name"],
                label=meta["label"],
                kind="numeric",
                defaultValue=schema.numeric_medians.get(meta["name"], meta.get("defaultValue", 0)),
                description=meta["description"],
            )
            for meta in NUMERIC_FIELD_META
        ]
        return FeatureSchemaResponse(
            genres=schema.genres,
            languages=schema.languages,
            numericFields=numeric_fields,
            featureCount=len(schema.feature_columns),
            referenceYear=schema.reference_year,
        )

    # ── predict ─────────────────────────────────────────────

    def predict(self, request: RevenuePredictionRequest) -> RevenuePredictionResponse:
        if request.movieName:
            return self._predict_from_name(request.movieName)
        if request.features:
            return self._predict_from_features(request.features)
        raise HTTPException(status_code=400, detail="Provide either movieName or features.")

    def _predict_from_name(self, movie_name: str) -> RevenuePredictionResponse:
        frame = load_csv(MOVIES_FILE)
        records = frame.to_dict("records")

        matched = _fuzzy_match(movie_name, records)
        if matched is None:
            raise HTTPException(
                status_code=404,
                detail=f"No movie found matching '{movie_name}'. Try a more specific title.",
            )

        movie_df = pd.DataFrame([matched])
        return self._run_prediction(movie_df, matched)

    def _predict_from_features(self, features: dict[str, Any]) -> RevenuePredictionResponse:
        schema = self.predictor.schema

        # Build a single-row dict with all columns the predictor expects
        row: dict[str, Any] = {
            "movie_id": 0,
            "title_clean": "Custom Input",
            "movie_year": None,
            "runtime_minutes": None,
            "tmdb_popularity": None,
            "budget": None,
            "rating_count": None,
            "rating_mean": None,
            "rating_median": None,
            "tag_count": None,
            "genres_json": "[]",
            "original_language": "en",
            "revenue": 0,
        }

        # Override with user-provided values
        for key, value in features.items():
            if value is not None and value != "":
                row[key] = value

        # Handle genres — accept as list or JSON string
        if "genres" in features:
            g = features["genres"]
            if isinstance(g, list):
                row["genres_json"] = json.dumps(g)
            elif isinstance(g, str):
                row["genres_json"] = g if g.startswith("[") else json.dumps([g])

        # Handle language
        if "original_language" in features:
            row["original_language"] = str(features["original_language"])

        movie_df = pd.DataFrame([row])
        return self._run_prediction(movie_df, row)

    def _run_prediction(
        self, movie_df: pd.DataFrame, row: dict[str, Any]
    ) -> RevenuePredictionResponse:
        result_df = self.predictor.predict_frame(movie_df)
        record = result_df.iloc[0]

        metrics = self._load_metrics()

        predicted = float(record["predicted_revenue"])
        xgb_pred = float(record["xgboost_predicted_revenue"])
        lgb_pred = float(record["lightgbm_predicted_revenue"])

        movie_id = int(record["movie_id"]) if pd.notna(record.get("movie_id")) else None
        movie_name = str(row.get("title_clean") or row.get("title") or "Custom Input")
        movie_year = int(record["movie_year"]) if pd.notna(record.get("movie_year")) else None

        revenue_val = record.get("revenue")
        actual = float(revenue_val) if pd.notna(revenue_val) and float(revenue_val) > 0 else None

        weights = self.predictor.weights

        return RevenuePredictionResponse(
            movieId=movie_id if movie_id and movie_id > 0 else None,
            movieName=movie_name,
            movieYear=movie_year,
            predictedRevenue=predicted,
            predictedRevenueFormatted=_format_money(predicted),
            xgboostPredictedRevenue=xgb_pred,
            xgboostPredictedRevenueFormatted=_format_money(xgb_pred),
            lightgbmPredictedRevenue=lgb_pred,
            lightgbmPredictedRevenueFormatted=_format_money(lgb_pred),
            ensembleWeights=EnsembleWeights(
                xgboost=round(weights["xgboost"], 4),
                lightgbm=round(weights["lightgbm"], 4),
            ),
            modelMetrics=ModelMetrics(
                rmseLog=round(metrics["rmseLog"], 4),
                maeLog=round(metrics["maeLog"], 4),
                r2Log=round(metrics["r2Log"], 4),
            ),
            actualRevenue=actual,
            actualRevenueFormatted=_format_money(actual) if actual is not None else None,
            featureCount=int(metrics.get("featureCount", 66)),
        )

    @staticmethod
    def _load_metrics() -> dict[str, Any]:
        metrics_path = MODELS_DIR / "artifacts" / "revenue_prediction" / "metrics.json"
        if not metrics_path.exists():
            return {"rmseLog": 0.0, "maeLog": 0.0, "r2Log": 0.0, "featureCount": 0}

        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        ensemble_metrics = payload.get("ensemble", {}).get("metrics", {})
        return {
            "rmseLog": ensemble_metrics.get("rmse_log", 0.0),
            "maeLog": ensemble_metrics.get("mae_log", 0.0),
            "r2Log": ensemble_metrics.get("r2_log", 0.0),
            "featureCount": payload.get("feature_count", 66),
        }


def get_revenue_service() -> RevenueService:
    return RevenueService()
