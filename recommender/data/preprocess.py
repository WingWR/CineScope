from __future__ import annotations

import json
import math
import re
from typing import Any

import pandas as pd

from recommender.core.exceptions import MovieNotFoundError


def parse_json_list(value: Any) -> list[str]:
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


def normalize_title(title: Any) -> str:
    text = "" if title is None else str(title)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def find_movie_index(movies: pd.DataFrame, movie_name: str) -> int:
    normalized = normalize_title(movie_name)
    if not normalized:
        raise MovieNotFoundError("Movie name cannot be empty.")

    titles = movies["title_clean"].map(normalize_title)
    exact_matches = movies.index[titles == normalized].tolist()
    if exact_matches:
        return int(exact_matches[0])

    contains_matches = movies.index[titles.str.contains(re.escape(normalized), na=False)].tolist()
    if contains_matches:
        return int(contains_matches[0])

    reverse_contains = movies.index[titles.map(lambda value: value and value in normalized)].tolist()
    if reverse_contains:
        return int(reverse_contains[0])

    raise MovieNotFoundError(f"Movie not found: {movie_name}")


def movie_to_item(
    movies: pd.DataFrame,
    movie_id: int,
    score: float,
    reason: str,
    source: str,
) -> dict[str, object]:
    row = movies.loc[movies["movie_id"].astype(int) == int(movie_id)]
    if row.empty:
        return {
            "movie_id": int(movie_id),
            "title": str(movie_id),
            "score": float(score),
            "reason": reason,
            "source": source,
            "movie_year": None,
            "genres": [],
        }

    record = row.iloc[0]
    year = pd.to_numeric(record.get("movie_year"), errors="coerce")
    return {
        "movie_id": int(movie_id),
        "title": str(record.get("title_clean", movie_id)),
        "score": round(float(score), 6),
        "reason": reason,
        "source": source,
        "movie_year": None if pd.isna(year) else float(year),
        "genres": parse_json_list(record.get("genres_json")),
    }

