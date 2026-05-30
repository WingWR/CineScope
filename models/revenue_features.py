from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TARGET_COLUMN = "revenue"
GENRE_COLUMN = "genres_json"
LANGUAGE_COLUMN = "original_language"

RAW_NUMERIC_COLUMNS = [
    "movie_year",
    "runtime_minutes",
    "tmdb_popularity",
    "budget",
    "rating_count",
    "rating_mean",
    "rating_median",
    "tag_count",
]

DERIVED_NUMERIC_FEATURES = [
    "movie_year",
    "release_age",
    "runtime_minutes",
    "tmdb_popularity",
    "log_tmdb_popularity",
    "budget",
    "log_budget",
    "has_budget",
    "rating_count",
    "log_rating_count",
    "rating_mean",
    "rating_median",
    "tag_count",
    "log_tag_count",
]


@dataclass(frozen=True)
class RevenueFeatureSchema:
    numeric_features: list[str]
    numeric_medians: dict[str, float]
    languages: list[str]
    language_feature_names: dict[str, str]
    genres: list[str]
    genre_feature_names: dict[str, str]
    feature_columns: list[str]
    reference_year: int
    target_column: str = TARGET_COLUMN
    target_transform: str = "log1p"


def filter_revenue_training_rows(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    filtered[TARGET_COLUMN] = pd.to_numeric(filtered[TARGET_COLUMN], errors="coerce")
    filtered = filtered[np.isfinite(filtered[TARGET_COLUMN]) & (filtered[TARGET_COLUMN] > 0)]
    return filtered.reset_index(drop=True)


def make_revenue_target(df: pd.DataFrame) -> np.ndarray:
    revenue = pd.to_numeric(df[TARGET_COLUMN], errors="coerce").to_numpy(dtype=float)
    return np.log1p(revenue)


def fit_revenue_feature_schema(df: pd.DataFrame) -> RevenueFeatureSchema:
    reference_year = _reference_year(df)
    numeric_frame = _make_numeric_features(df, reference_year)
    medians = {
        column: _safe_median(numeric_frame[column])
        for column in DERIVED_NUMERIC_FEATURES
    }

    languages = sorted({_normalize_language(value) for value in df.get(LANGUAGE_COLUMN, [])})
    genres = sorted({genre for value in df.get(GENRE_COLUMN, []) for genre in parse_genres(value)})

    used_names = set(DERIVED_NUMERIC_FEATURES)
    language_feature_names = {
        language: _safe_feature_name("lang", language, used_names)
        for language in languages
    }
    genre_feature_names = {
        genre: _safe_feature_name("genre", genre, used_names)
        for genre in genres
    }

    feature_columns = (
        list(DERIVED_NUMERIC_FEATURES)
        + [language_feature_names[language] for language in languages]
        + [genre_feature_names[genre] for genre in genres]
    )
    return RevenueFeatureSchema(
        numeric_features=list(DERIVED_NUMERIC_FEATURES),
        numeric_medians=medians,
        languages=languages,
        language_feature_names=language_feature_names,
        genres=genres,
        genre_feature_names=genre_feature_names,
        feature_columns=feature_columns,
        reference_year=reference_year,
    )


def transform_revenue_features(df: pd.DataFrame, schema: RevenueFeatureSchema) -> pd.DataFrame:
    numeric_frame = _make_numeric_features(df, schema.reference_year)
    output = pd.DataFrame(index=df.index)

    for column in schema.numeric_features:
        median_value = schema.numeric_medians.get(column, 0.0)
        output[column] = numeric_frame[column].fillna(median_value)

    languages = df.get(LANGUAGE_COLUMN, pd.Series(["unknown"] * len(df), index=df.index))
    normalized_languages = languages.map(_normalize_language)
    for language in schema.languages:
        feature_name = schema.language_feature_names[language]
        output[feature_name] = (normalized_languages == language).astype(float)

    genre_sets = df.get(GENRE_COLUMN, pd.Series(["[]"] * len(df), index=df.index)).map(
        lambda value: set(parse_genres(value))
    )
    for genre in schema.genres:
        feature_name = schema.genre_feature_names[genre]
        output[feature_name] = genre_sets.map(lambda values: float(genre in values))

    return output.reindex(columns=schema.feature_columns, fill_value=0.0).astype("float32")


def save_revenue_feature_schema(schema: RevenueFeatureSchema, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(schema), ensure_ascii=False, indent=2), encoding="utf-8")


def load_revenue_feature_schema(path: str | Path) -> RevenueFeatureSchema:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RevenueFeatureSchema(**payload)


def parse_genres(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).strip() for item in parsed if str(item).strip()]


def _make_numeric_features(df: pd.DataFrame, reference_year: int) -> pd.DataFrame:
    numeric = pd.DataFrame(index=df.index)
    for column in RAW_NUMERIC_COLUMNS:
        if column in df:
            numeric[column] = pd.to_numeric(df[column], errors="coerce")
        else:
            numeric[column] = np.nan

    output = pd.DataFrame(index=df.index)
    output["movie_year"] = numeric["movie_year"]
    output["release_age"] = reference_year - numeric["movie_year"]
    output["runtime_minutes"] = numeric["runtime_minutes"]
    output["tmdb_popularity"] = numeric["tmdb_popularity"].clip(lower=0)
    output["log_tmdb_popularity"] = np.log1p(output["tmdb_popularity"])
    output["budget"] = numeric["budget"].clip(lower=0)
    output["log_budget"] = np.log1p(output["budget"])
    output["has_budget"] = (output["budget"] > 0).astype(float)
    output["rating_count"] = numeric["rating_count"].clip(lower=0)
    output["log_rating_count"] = np.log1p(output["rating_count"])
    output["rating_mean"] = numeric["rating_mean"]
    output["rating_median"] = numeric["rating_median"]
    output["tag_count"] = numeric["tag_count"].clip(lower=0)
    output["log_tag_count"] = np.log1p(output["tag_count"])
    return output


def _reference_year(df: pd.DataFrame) -> int:
    if "movie_year" not in df:
        return 2026
    years = pd.to_numeric(df["movie_year"], errors="coerce")
    years = years[np.isfinite(years)]
    years = years[(years >= 1800) & (years <= 2100)]
    if years.empty:
        return 2026
    return int(years.max())


def _safe_median(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce")
    values = values[np.isfinite(values)]
    if values.empty:
        return 0.0
    return float(values.median())


def _normalize_language(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "unknown"
    text = str(value).strip().lower()
    return text or "unknown"


def _safe_feature_name(prefix: str, value: str, used_names: set[str]) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", value.lower()).strip("_")
    cleaned = cleaned or "unknown"
    base = f"{prefix}_{cleaned}"
    name = base
    suffix = 2
    while name in used_names:
        name = f"{base}_{suffix}"
        suffix += 1
    used_names.add(name)
    return name
