from __future__ import annotations

from typing import Any

import pandas as pd

from server.app.modules.movies.schemas import Movie
from server.app.shared.text_utils import normalize_text, parse_json_list


def movie_record_to_schema(record: dict[str, Any]) -> Movie:
    genres = record.get("genres")
    tags = record.get("tags")

    return Movie(
        id=_coerce_int(record.get("movie_id")) or normalize_text(record.get("movie_id")),
        title=normalize_text(record.get("title_clean")) or "Untitled",
        year=_coerce_int(record.get("movie_year")),
        genres=genres if isinstance(genres, list) else parse_json_list(record.get("genres_json")),
        ratingMean=_coerce_float(record.get("rating_mean")),
        ratingCount=_coerce_int(record.get("rating_count")),
        tagCount=_coerce_int(record.get("tag_count")),
        tags=tags if isinstance(tags, list) else parse_json_list(record.get("top_tags_json")),
        overview=normalize_text(record.get("overview")) or None,
        runtimeMinutes=_coerce_int(record.get("runtime_minutes")),
        tmdbPopularity=_coerce_float(record.get("tmdb_popularity")),
        budget=_coerce_float(record.get("budget")),
        revenue=_coerce_float(record.get("revenue")),
        language=normalize_text(record.get("original_language")) or None,
        posterUrl=normalize_text(record.get("poster_url")) or None,
        backdropUrl=normalize_text(record.get("backdrop_url")) or None,
    )


def _coerce_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _coerce_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(float(value))
