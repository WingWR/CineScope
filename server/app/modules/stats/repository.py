from __future__ import annotations

from typing import Any

import pandas as pd

from server.app.core.paths import DATASET_SUMMARY_FILE, GENRE_STATS_FILE, MOVIES_FILE
from server.app.shared.cache import cached
from server.app.shared.csv_loader import load_csv
from server.app.shared.json_loader import load_json


class StatsRepository:
    def load_summary(self) -> dict[str, Any]:
        return dict(_load_summary())

    def load_genres(self) -> list[dict[str, Any]]:
        return [dict(record) for record in _load_genres()]

    def load_movies(self) -> pd.DataFrame:
        return _load_movies().copy()


@cached
def _load_summary() -> dict[str, Any]:
    return load_json(DATASET_SUMMARY_FILE)


@cached
def _load_genres() -> list[dict[str, Any]]:
    frame = load_csv(GENRE_STATS_FILE)
    frame["movie_count"] = pd.to_numeric(frame["movie_count"], errors="coerce").fillna(0).astype(int)
    return frame.to_dict("records")


@cached
def _load_movies() -> pd.DataFrame:
    frame = load_csv(MOVIES_FILE)
    numeric_columns = [
        "movie_year",
        "rating_mean",
        "rating_count",
        "tmdb_popularity",
        "budget",
        "revenue",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame
