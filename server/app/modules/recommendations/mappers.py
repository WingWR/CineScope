from __future__ import annotations

from typing import Any

import pandas as pd

from server.app.modules.movies.mappers import movie_record_to_schema
from server.app.modules.movies.repository import MovieRepository
from server.app.modules.movies.schemas import Movie
from server.app.modules.recommendations.schemas import RecommendationItem
from server.app.shared.text_utils import normalize_text


_MOVIE_REPOSITORY = MovieRepository()
_SOURCE_MAP = {
    "content_based": "content",
    "content": "content",
    "collaborative": "collaborative",
    "user_knn": "collaborative",
    "item_knn": "collaborative",
    "hybrid": "hybrid",
}


def recommender_item_to_schema(item: dict[str, Any]) -> RecommendationItem:
    movie_id = _coerce_int(item.get("movie_id"))
    record = _MOVIE_REPOSITORY.get_record_by_id(movie_id) if movie_id is not None else None
    movie = movie_record_to_schema(record) if record is not None else Movie(
        id=movie_id or normalize_text(item.get("movie_id")) or normalize_text(item.get("title")) or "unknown",
        title=normalize_text(item.get("title")) or "Untitled",
        year=_coerce_int(item.get("movie_year")),
        genres=_coerce_str_list(item.get("genres")),
    )
    return RecommendationItem(
        movie=movie,
        score=round(_coerce_float(item.get("score")) or 0.0, 6),
        reason=normalize_text(item.get("reason")) or "Recommended by the ranking pipeline.",
        source=_map_source(item.get("source")),
    )


def _map_source(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return "content"
    lowered = text.lower()
    return _SOURCE_MAP.get(lowered, text)


def _coerce_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _coerce_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(float(value))


def _coerce_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalize_text(item) for item in value if normalize_text(item)]
