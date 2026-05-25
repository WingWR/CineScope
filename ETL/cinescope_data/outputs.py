from __future__ import annotations

from typing import Any

import pandas as pd

from .config import FINAL_DIR
from .submission import apply_submission_metadata, prepare_submission_frames, remove_non_submission_files
from .utils import json_dumps, missing_or_blank_count


def write_final_outputs(
    enriched: pd.DataFrame,
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    features: pd.DataFrame,
    genre_frame: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    final_movies = enriched[enriched["tmdb_id"].notna() & enriched["has_tmdb_detail"]].copy()
    final_movies["tmdb_id"] = final_movies["tmdb_id"].astype(int)

    final_movie_ids = set(final_movies["movie_id"])
    final_ratings = ratings[ratings["movie_id"].isin(final_movie_ids)].copy()
    final_tags = tags[tags["movie_id"].isin(final_movie_ids)].copy()

    final_genre_frame = genre_frame[genre_frame["movie_id"].isin(final_movie_ids)].copy()
    final_genre_stats = (
        final_genre_frame.groupby("genre")
        .size()
        .reset_index(name="movie_count")
        .sort_values("movie_count", ascending=False)
        if not final_genre_frame.empty
        else pd.DataFrame(columns=["genre", "movie_count"])
    )

    duplicate_tmdb_records = (
        final_movies[final_movies["tmdb_id"].duplicated(keep=False)]
        .sort_values(["tmdb_id", "movie_id"])[["movie_id", "tmdb_id", "title", "display_title"]]
        .to_dict("records")
    )

    submission_movies, submission_ratings, submission_tags, submission_genre_stats = prepare_submission_frames(
        movies=final_movies,
        ratings=final_ratings,
        tags=final_tags,
        genre_stats=final_genre_stats,
    )

    submission_movies.to_csv(FINAL_DIR / "movies.csv", index=False)
    submission_ratings.to_csv(FINAL_DIR / "ratings.csv", index=False)
    submission_tags.to_csv(FINAL_DIR / "tags.csv", index=False)
    submission_genre_stats.to_csv(FINAL_DIR / "genre_stats.csv", index=False)
    remove_non_submission_files(FINAL_DIR)

    summary = {
        "dataset": dataset_name,
        "scope": "movies_with_tmdb_detail",
        "movie_count": int(len(final_movies)),
        "user_count": int(final_ratings["user_id"].nunique()),
        "rating_count": int(len(final_ratings)),
        "tag_count": int(len(final_tags)),
        "genre_count": int(final_genre_stats["genre"].nunique()) if not final_genre_stats.empty else 0,
        "rating_mean": float(final_ratings["rating"].mean()),
        "rating_min": float(final_ratings["rating"].min()),
        "rating_max": float(final_ratings["rating"].max()),
        "movie_with_tmdb_id_count": int(final_movies["tmdb_id"].notna().sum()),
        "movie_with_tmdb_detail_count": int(final_movies["has_tmdb_detail"].sum()),
    }
    quality_report = {
        "scope": "Movies with non-null tmdb_id and successful TMDb detail match",
        "source_movie_count": int(len(enriched)),
        "final_movie_count": int(len(final_movies)),
        "source_movie_with_tmdb_id_count": int(enriched["tmdb_id"].notna().sum()),
        "source_movie_with_tmdb_detail_count": int(enriched["has_tmdb_detail"].sum()),
        "dropped_movie_without_tmdb_id_count": int(enriched["tmdb_id"].isna().sum()),
        "dropped_movie_without_tmdb_detail_count": int(
            (enriched["tmdb_id"].notna() & ~enriched["has_tmdb_detail"]).sum()
        ),
        "dropped_rating_without_tmdb_id_movie_count": int(len(ratings) - len(final_ratings)),
        "dropped_tag_without_tmdb_id_movie_count": int(len(tags) - len(final_tags)),
        "tmdb_detail_count": int(final_movies["has_tmdb_detail"].sum()),
        "tmdb_detail_missing_count": int((~final_movies["has_tmdb_detail"]).sum()),
        "tmdb_movie_endpoint_count": int((final_movies["tmdb_media_type"] == "movie").sum()),
        "tmdb_tv_endpoint_count": int((final_movies["tmdb_media_type"] == "tv").sum()),
        "tmdb_resolved_from_imdb_id_count": int(final_movies["tmdb_resolved_from_imdb_id"].notna().sum()),
        "movie_id_is_unique": bool(final_movies["movie_id"].is_unique),
        "tmdb_id_missing_count": int(final_movies["tmdb_id"].isna().sum()),
        "tmdb_id_duplicate_row_count": int(final_movies["tmdb_id"].duplicated(keep=False).sum()),
        "tmdb_id_duplicate_records": duplicate_tmdb_records,
        "overview_missing_count": missing_or_blank_count(final_movies, "overview"),
        "runtime_minutes_missing_count": int(final_movies["runtime_minutes"].isna().sum()),
        "poster_url_missing_count": missing_or_blank_count(final_movies, "poster_url"),
        "backdrop_url_missing_count": missing_or_blank_count(final_movies, "backdrop_url"),
    }
    apply_submission_metadata(quality_report)

    (FINAL_DIR / "dataset_summary.json").write_text(json_dumps(summary), encoding="utf-8")
    (FINAL_DIR / "quality_report.json").write_text(json_dumps(quality_report), encoding="utf-8")
    return quality_report

