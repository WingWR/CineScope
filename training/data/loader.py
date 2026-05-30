from __future__ import annotations

from pathlib import Path

import pandas as pd

from models.data_loader import load_movies
from models.revenue_features import TARGET_COLUMN
from training.config import DATA_FILE


REQUIRED_COLUMNS = {
    "movie_id",
    "title_clean",
    "movie_year",
    "genres_json",
    "rating_count",
    "rating_mean",
    "rating_median",
    "tag_count",
    "runtime_minutes",
    "tmdb_popularity",
    "budget",
    TARGET_COLUMN,
    "original_language",
}


def load_revenue_training_source(path: str | Path | None = None) -> pd.DataFrame:
    df = load_movies(path or DATA_FILE)
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"movies.csv is missing required columns: {missing}")
    return df
