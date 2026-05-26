from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import FINAL_DIR, RAW_DIR
from .utils import json_dumps


MOVIELENS_METADATA_PATH = RAW_DIR / "movielens_metadata" / "movies_metadata.csv"
MOVIELENS_METADATA_COLUMNS = ["id", "imdb_id", "budget", "revenue"]
FINANCIAL_COLUMNS = ["budget", "revenue"]

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
    "budget",
    "revenue",
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


def load_financial_metadata(
    metadata_path: Path = MOVIELENS_METADATA_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    if not metadata_path.exists():
        empty = pd.DataFrame(columns=["tmdb_id", *FINANCIAL_COLUMNS])
        empty_imdb = pd.DataFrame(columns=["imdb_tt_id", *FINANCIAL_COLUMNS])
        return empty, empty_imdb, {
            "metadata_rows": 0,
            "metadata_valid_tmdb_id_rows": 0,
            "metadata_duplicate_tmdb_id_rows": 0,
            "metadata_deduplicated_rows": 0,
        }, empty_imdb

    metadata = pd.read_csv(metadata_path, usecols=MOVIELENS_METADATA_COLUMNS, low_memory=False)
    metadata["tmdb_id"] = pd.to_numeric(metadata["id"], errors="coerce")
    metadata["budget"] = pd.to_numeric(metadata["budget"], errors="coerce").fillna(0).astype("int64")
    metadata["revenue"] = pd.to_numeric(metadata["revenue"], errors="coerce").fillna(0).astype("int64")
    metadata["financial_signal_count"] = metadata["budget"].gt(0).astype(int) + metadata["revenue"].gt(0).astype(int)

    valid_metadata = metadata[metadata["tmdb_id"].notna()].copy()
    valid_metadata["tmdb_id"] = valid_metadata["tmdb_id"].astype("int64")
    duplicate_tmdb_id_rows = int(valid_metadata["tmdb_id"].duplicated(keep=False).sum())

    deduplicated_by_tmdb = (
        valid_metadata.sort_values(
            ["tmdb_id", "financial_signal_count", "budget", "revenue"],
            ascending=[True, False, False, False],
        )
        .drop_duplicates("tmdb_id", keep="first")
        .loc[:, ["tmdb_id", "budget", "revenue"]]
    )

    valid_imdb_metadata = metadata[metadata["imdb_id"].notna()].copy()
    duplicate_imdb_id_rows = int(valid_imdb_metadata["imdb_id"].duplicated(keep=False).sum())
    deduplicated_by_imdb = (
        valid_imdb_metadata.sort_values(
            ["imdb_id", "financial_signal_count", "budget", "revenue"],
            ascending=[True, False, False, False],
        )
        .drop_duplicates("imdb_id", keep="first")
        .rename(columns={"imdb_id": "imdb_tt_id"})
        .loc[:, ["imdb_tt_id", "budget", "revenue"]]
    )

    stats = {
        "metadata_rows": int(len(metadata)),
        "metadata_valid_tmdb_id_rows": int(len(valid_metadata)),
        "metadata_duplicate_tmdb_id_rows": duplicate_tmdb_id_rows,
        "metadata_deduplicated_rows": int(len(deduplicated_by_tmdb)),
        "metadata_valid_imdb_id_rows": int(len(valid_imdb_metadata)),
        "metadata_duplicate_imdb_id_rows": duplicate_imdb_id_rows,
        "metadata_deduplicated_imdb_rows": int(len(deduplicated_by_imdb)),
    }
    return deduplicated_by_tmdb, deduplicated_by_imdb, stats


def attach_financial_metadata(
    movies: pd.DataFrame,
    metadata_path: Path = MOVIELENS_METADATA_PATH,
) -> tuple[pd.DataFrame, dict[str, int]]:
    enriched_movies = movies.drop(columns=FINANCIAL_COLUMNS, errors="ignore").copy()
    financial_metadata, financial_metadata_by_imdb, metadata_stats = load_financial_metadata(metadata_path)
    if financial_metadata.empty:
        enriched_movies["budget"] = 0
        enriched_movies["revenue"] = 0
        tmdb_matched_count = 0
        imdb_fallback_matched_count = 0
        matched_count = 0
    else:
        enriched_movies = enriched_movies.merge(financial_metadata, on="tmdb_id", how="left")
        tmdb_matched_count = int(enriched_movies["budget"].notna().sum())
        if financial_metadata_by_imdb.empty:
            imdb_fallback_matched_count = 0
        else:
            fallback_metadata = financial_metadata_by_imdb.rename(
                columns={"budget": "budget_imdb", "revenue": "revenue_imdb"}
            )
            enriched_movies = enriched_movies.merge(fallback_metadata, on="imdb_tt_id", how="left")
            needs_fallback = enriched_movies["budget"].isna()
            imdb_fallback_matched = needs_fallback & enriched_movies["budget_imdb"].notna()
            imdb_fallback_matched_count = int(imdb_fallback_matched.sum())
            enriched_movies.loc[imdb_fallback_matched, "budget"] = enriched_movies.loc[
                imdb_fallback_matched, "budget_imdb"
            ]
            enriched_movies.loc[imdb_fallback_matched, "revenue"] = enriched_movies.loc[
                imdb_fallback_matched, "revenue_imdb"
            ]
            enriched_movies = enriched_movies.drop(columns=["budget_imdb", "revenue_imdb"])

        matched_count = int(enriched_movies["budget"].notna().sum())
        enriched_movies["budget"] = enriched_movies["budget"].fillna(0).astype("int64")
        enriched_movies["revenue"] = enriched_movies["revenue"].fillna(0).astype("int64")

    finance_stats = {
        **metadata_stats,
        "financial_metadata_tmdb_matched_movie_count": tmdb_matched_count,
        "financial_metadata_imdb_fallback_matched_movie_count": imdb_fallback_matched_count,
        "financial_metadata_matched_movie_count": matched_count,
        "financial_metadata_unmatched_movie_count": int(len(enriched_movies) - matched_count),
        "budget_nonzero_count": int(enriched_movies["budget"].gt(0).sum()),
        "revenue_nonzero_count": int(enriched_movies["revenue"].gt(0).sum()),
        "budget_revenue_both_nonzero_count": int(
            (enriched_movies["budget"].gt(0) & enriched_movies["revenue"].gt(0)).sum()
        ),
    }
    return enriched_movies, finance_stats


def prepare_submission_frames(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    genre_stats: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int]]:
    movies_with_finance, finance_stats = attach_financial_metadata(movies)
    require_columns(movies_with_finance, MOVIES_SUBMISSION_COLUMNS, "movies.csv")
    submission_movies = movies_with_finance.loc[:, MOVIES_SUBMISSION_COLUMNS].copy()
    submission_ratings = ratings.copy()
    submission_tags = tags.drop(columns=[column for column in TAGS_DROP_COLUMNS if column in tags.columns]).copy()
    submission_genre_stats = genre_stats.copy()
    return submission_movies, submission_ratings, submission_tags, submission_genre_stats, finance_stats


def remove_non_submission_files(final_dir: Path = FINAL_DIR) -> None:
    for file_name in REMOVED_FINAL_FILES:
        file_path = final_dir / file_name
        if file_path.exists():
            file_path.unlink()


def annotate_submission_metadata(final_dir: Path = FINAL_DIR, finance_stats: dict[str, int] | None = None) -> None:
    quality_path = final_dir / "quality_report.json"
    if not quality_path.exists():
        return

    quality_report = json.loads(quality_path.read_text(encoding="utf-8"))
    apply_submission_metadata(quality_report, finance_stats)
    quality_path.write_text(json_dumps(quality_report), encoding="utf-8")


def apply_submission_metadata(quality_report: dict, finance_stats: dict[str, int] | None = None) -> None:
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
    if finance_stats is not None:
        quality_report.update(finance_stats)


def rewrite_existing_final_for_submission(final_dir: Path = FINAL_DIR) -> None:
    movies = pd.read_csv(final_dir / "movies.csv")
    ratings = pd.read_csv(final_dir / "ratings.csv")
    tags = pd.read_csv(final_dir / "tags.csv")
    genre_stats = pd.read_csv(final_dir / "genre_stats.csv")

    submission_movies, submission_ratings, submission_tags, submission_genre_stats, finance_stats = prepare_submission_frames(
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
    annotate_submission_metadata(final_dir, finance_stats)
