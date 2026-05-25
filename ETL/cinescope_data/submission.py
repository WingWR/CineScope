from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import FINAL_DIR
from .utils import json_dumps


MOVIES_SUBMISSION_COLUMNS = [
    "movie_id",
    "title_clean",
    "movie_year",
    "genres_json",
    "imdb_id",
    "tmdb_id",
    "imdb_tt_id",
    "rating_count",
    "rating_mean",
    "rating_median",
    "tag_count",
    "top_tags_json",
    "overview",
    "runtime_minutes",
    "tmdb_popularity",
    "original_language",
    "poster_url",
    "backdrop_url",
]

TAGS_DROP_COLUMNS = ["tag"]
REMOVED_FINAL_FILES = ["movie_features.csv"]
NON_SUBMISSION_QUALITY_KEYS = [
    "display_title_missing_count",
    "display_year_missing_count",
    "search_text_missing_count",
    "feature_text_missing_count",
]


def require_columns(frame: pd.DataFrame, columns: list[str], frame_name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"{frame_name} is missing required columns: {missing_text}")


def prepare_submission_frames(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    genre_stats: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    require_columns(movies, MOVIES_SUBMISSION_COLUMNS, "movies.csv")
    submission_movies = movies.loc[:, MOVIES_SUBMISSION_COLUMNS].copy()
    submission_ratings = ratings.copy()
    submission_tags = tags.drop(columns=[column for column in TAGS_DROP_COLUMNS if column in tags.columns]).copy()
    submission_genre_stats = genre_stats.copy()
    return submission_movies, submission_ratings, submission_tags, submission_genre_stats


def remove_non_submission_files(final_dir: Path = FINAL_DIR) -> None:
    for file_name in REMOVED_FINAL_FILES:
        file_path = final_dir / file_name
        if file_path.exists():
            file_path.unlink()


def annotate_submission_metadata(final_dir: Path = FINAL_DIR) -> None:
    quality_path = final_dir / "quality_report.json"
    if not quality_path.exists():
        return

    quality_report = json.loads(quality_path.read_text(encoding="utf-8"))
    apply_submission_metadata(quality_report)
    quality_path.write_text(json_dumps(quality_report), encoding="utf-8")


def apply_submission_metadata(quality_report: dict) -> None:
    for key in NON_SUBMISSION_QUALITY_KEYS:
        quality_report.pop(key, None)

    quality_report["submission_scope"] = "RQ.md required CSV fields"
    quality_report["submitted_csv_files"] = [
        "movies.csv",
        "ratings.csv",
        "tags.csv",
        "genre_stats.csv",
    ]
    quality_report["removed_csv_files"] = REMOVED_FINAL_FILES
    quality_report["movies_submission_columns"] = MOVIES_SUBMISSION_COLUMNS
    quality_report["tags_removed_columns"] = TAGS_DROP_COLUMNS


def rewrite_existing_final_for_submission(final_dir: Path = FINAL_DIR) -> None:
    movies = pd.read_csv(final_dir / "movies.csv")
    ratings = pd.read_csv(final_dir / "ratings.csv")
    tags = pd.read_csv(final_dir / "tags.csv")
    genre_stats = pd.read_csv(final_dir / "genre_stats.csv")

    submission_movies, submission_ratings, submission_tags, submission_genre_stats = prepare_submission_frames(
        movies=movies,
        ratings=ratings,
        tags=tags,
        genre_stats=genre_stats,
    )

    submission_movies.to_csv(final_dir / "movies.csv", index=False)
    submission_ratings.to_csv(final_dir / "ratings.csv", index=False)
    submission_tags.to_csv(final_dir / "tags.csv", index=False)
    submission_genre_stats.to_csv(final_dir / "genre_stats.csv", index=False)
    remove_non_submission_files(final_dir)
    annotate_submission_metadata(final_dir)
