from __future__ import annotations

from typing import Any

import pandas as pd

from .config import PROCESSED_DIR, TmdbConfig
from .movielens import aggregate_ratings, aggregate_tags, parse_genres
from .outputs import write_final_outputs
from .tmdb_client import tmdb_cache_to_frame
from .utils import json_dumps


def weighted_rating(row: pd.Series, global_mean: float, min_votes: float) -> float:
    votes = row.get("rating_count", 0) or 0
    mean = row.get("rating_mean", 0) or 0
    if votes <= 0:
        return 0.0
    return float((votes / (votes + min_votes)) * mean + (min_votes / (votes + min_votes)) * global_mean)


def build_outputs(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    links: pd.DataFrame,
    tmdb_cache: dict[int, dict[str, Any]],
    config: TmdbConfig,
    dataset_name: str,
) -> None:
    rating_stats = aggregate_ratings(ratings)
    tag_stats = aggregate_tags(tags)
    tmdb_frame = tmdb_cache_to_frame(tmdb_cache, config)

    movie_base = movies.drop(columns=["genres_list"], errors="ignore")
    enriched = movie_base.merge(links, on="movie_id", how="left")
    enriched = enriched.merge(rating_stats, on="movie_id", how="left")
    enriched = enriched.merge(tag_stats, on="movie_id", how="left")
    if not tmdb_frame.empty:
        enriched = enriched.merge(tmdb_frame, on="tmdb_id", how="left")

    enriched["rating_count"] = enriched["rating_count"].fillna(0).astype(int)
    enriched["tag_count"] = enriched["tag_count"].fillna(0).astype(int)
    enriched["rating_mean"] = enriched["rating_mean"].fillna(0)
    enriched["rating_median"] = enriched["rating_median"].fillna(0)
    enriched["rating_std"] = enriched["rating_std"].fillna(0)
    enriched["top_tags_json"] = enriched["top_tags_json"].fillna("[]")
    enriched["tags_text"] = enriched["tags_text"].fillna("")

    enriched["display_title"] = enriched.get("tmdb_title", pd.Series(index=enriched.index, dtype=object)).fillna(
        enriched["title_clean"]
    )
    enriched["display_year"] = enriched.get("tmdb_year", pd.Series(index=enriched.index, dtype="Int64")).fillna(
        enriched["movie_year"]
    )
    enriched["display_year"] = pd.to_numeric(enriched["display_year"], errors="coerce").astype("Int64")
    enriched["has_tmdb_id"] = enriched["tmdb_id"].notna()
    enriched["has_tmdb_detail"] = enriched.get("tmdb_title", pd.Series(index=enriched.index)).notna()
    enriched["search_text"] = (
        enriched["display_title"].fillna("")
        + " "
        + enriched["title_clean"].fillna("")
        + " "
        + enriched["genres_text"].fillna("")
        + " "
        + enriched["tags_text"].fillna("")
        + " "
        + enriched.get("overview", pd.Series(index=enriched.index, dtype=object)).fillna("")
    ).str.lower()

    global_mean = ratings["rating"].mean()
    min_votes = rating_stats["rating_count"].quantile(0.8)
    enriched["weighted_rating"] = enriched.apply(
        lambda row: weighted_rating(row, global_mean=global_mean, min_votes=min_votes), axis=1
    )

    for column, fallback in [
        ("tmdb_vote_average", "rating_mean"),
        ("tmdb_vote_count", "rating_count"),
        ("tmdb_popularity", "rating_count"),
    ]:
        if column not in enriched.columns:
            enriched[column] = enriched[fallback]
        else:
            enriched[column] = enriched[column].fillna(enriched[fallback])

    genre_rows = []
    for _, row in movies.iterrows():
        for genre in parse_genres(row["genres"]):
            genre_rows.append({"movie_id": row["movie_id"], "genre": genre})
    genre_frame = pd.DataFrame(genre_rows)
    genre_stats = (
        genre_frame.groupby("genre").size().reset_index(name="movie_count").sort_values("movie_count", ascending=False)
        if not genre_frame.empty
        else pd.DataFrame(columns=["genre", "movie_count"])
    )

    features = enriched[
        [
            "movie_id",
            "display_title",
            "display_year",
            "genres_json",
            "top_tags_json",
            "rating_count",
            "rating_mean",
            "weighted_rating",
            "tmdb_vote_average",
            "tmdb_vote_count",
            "tmdb_popularity",
            "search_text",
        ]
    ].copy()
    features.columns = [
        "movie_id",
        "display_title",
        "display_year",
        "genres_json",
        "top_tags_json",
        "rating_count",
        "rating_mean",
        "weighted_rating",
        "tmdb_vote_average",
        "tmdb_vote_count",
        "tmdb_popularity",
        "feature_text",
    ]

    if not genre_frame.empty:
        genre_one_hot = pd.crosstab(genre_frame["movie_id"], genre_frame["genre"])
        genre_one_hot = genre_one_hot.add_prefix("genre_").reset_index()
        features = features.merge(genre_one_hot, on="movie_id", how="left").fillna(0)

    ratings.to_csv(PROCESSED_DIR / "ratings_clean.csv", index=False)
    tags.to_csv(PROCESSED_DIR / "tags_clean.csv", index=False)
    enriched.to_csv(PROCESSED_DIR / "movies_enriched.csv", index=False)
    features.to_csv(PROCESSED_DIR / "movie_features.csv", index=False)
    genre_stats.to_csv(PROCESSED_DIR / "genre_stats.csv", index=False)
    final_quality_report = write_final_outputs(
        enriched=enriched,
        ratings=ratings,
        tags=tags,
        features=features,
        genre_frame=genre_frame,
        dataset_name=dataset_name,
    )

    summary = {
        "dataset": dataset_name,
        "movie_count": int(movies["movie_id"].nunique()),
        "user_count": int(ratings["user_id"].nunique()),
        "rating_count": int(len(ratings)),
        "tag_count": int(len(tags)),
        "movie_with_tmdb_id_count": int(links["tmdb_id"].notna().sum()),
        "movie_with_tmdb_detail_count": int(enriched["has_tmdb_detail"].sum()),
        "genre_count": int(genre_stats["genre"].nunique()) if not genre_stats.empty else 0,
        "rating_mean": float(ratings["rating"].mean()),
        "rating_min": float(ratings["rating"].min()),
        "rating_max": float(ratings["rating"].max()),
        "final_movie_count": final_quality_report["final_movie_count"],
    }
    (PROCESSED_DIR / "dataset_summary.json").write_text(json_dumps(summary), encoding="utf-8")
    print(f"Wrote processed files to {PROCESSED_DIR}")

