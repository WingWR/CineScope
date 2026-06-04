from __future__ import annotations

from typing import Any

import pandas as pd

from server.app.core.paths import MOVIES_FILE
from server.app.shared.cache import cached
from server.app.shared.csv_loader import load_csv
from server.app.shared.text_utils import normalize_text, parse_json_list


class MovieRepository:
    def list_records(self) -> list[dict[str, Any]]:
        return _load_movie_records()

    def get_record_by_id(self, movie_id: int | str) -> dict[str, Any] | None:
        return _movie_records_by_id().get(_normalize_movie_id(movie_id))


@cached
def _load_movie_records() -> list[dict[str, Any]]:
    frame = load_csv(MOVIES_FILE)
    numeric_columns = [
        "movie_id",
        "movie_year",
        "rating_count",
        "rating_mean",
        "rating_median",
        "tag_count",
        "runtime_minutes",
        "tmdb_popularity",
        "budget",
        "revenue",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    records: list[dict[str, Any]] = []
    for record in frame.to_dict("records"):
        movie_id = _coerce_int(record.get("movie_id"))
        if movie_id is None:
            continue

        title = normalize_text(record.get("title_clean"))
        overview = normalize_text(record.get("overview"))
        genres = parse_json_list(record.get("genres_json"))
        tags = parse_json_list(record.get("top_tags_json"))
        language = normalize_text(record.get("original_language")).lower()
        search_blob = " ".join(
            part
            for part in (
                title,
                overview,
                " ".join(genres),
                " ".join(tags),
            )
            if part
        ).lower()

        enriched = dict(record)
        enriched["movie_id"] = movie_id
        enriched["genres"] = genres
        enriched["tags"] = tags
        enriched["_title_norm"] = title.lower()
        enriched["_language_norm"] = language
        enriched["_search_blob"] = search_blob
        records.append(enriched)

    return records


@cached
def _movie_records_by_id() -> dict[str, dict[str, Any]]:
    return {str(record["movie_id"]): record for record in _load_movie_records()}


def _normalize_movie_id(movie_id: int | str) -> str:
    text = normalize_text(movie_id)
    if not text:
        return ""

    if text.isdigit():
        return str(int(text))

    try:
        return str(int(float(text)))
    except ValueError:
        return text


def _coerce_int(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(float(value))
