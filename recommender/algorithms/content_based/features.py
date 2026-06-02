from __future__ import annotations

import pandas as pd

from recommender.data.preprocess import parse_json_list


def build_overview_text(movies: pd.DataFrame) -> pd.Series:
    overview = movies.get("overview", pd.Series([""] * len(movies), index=movies.index))
    title = movies.get("title_clean", pd.Series([""] * len(movies), index=movies.index))
    return (title.fillna("") + " " + overview.fillna("")).str.strip()


def build_content_soup(movies: pd.DataFrame) -> pd.Series:
    rows: list[str] = []
    for _, row in movies.iterrows():
        tokens: list[str] = []
        tokens.append(str(row.get("title_clean", "") or ""))
        tokens.extend(parse_json_list(row.get("genres_json")))
        tokens.extend(parse_json_list(row.get("top_tags_json")))

        language = str(row.get("original_language", "") or "").strip()
        if language:
            tokens.append(f"language_{language}")

        # Add directors, actors, or keywords here if ETL later exposes them.
        for optional_field in ("director", "directors", "actors", "cast", "keywords"):
            if optional_field in movies.columns:
                tokens.extend(parse_json_list(row.get(optional_field)))

        rows.append(" ".join(_clean_token(token) for token in tokens if str(token).strip()))
    return pd.Series(rows, index=movies.index)


def _clean_token(token: object) -> str:
    return str(token).lower().replace(" ", "_").strip()

