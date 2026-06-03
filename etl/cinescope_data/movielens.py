from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .config import INTERIM_DIR
from .utils import json_dumps


NO_GENRES = "(no genres listed)"


def download_file(url: str, target: Path, force: bool = False) -> None:
    if target.exists() and not force:
        print(f"MovieLens archive exists: {target}")
        return
    print(f"Downloading {url}")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
    print(f"Downloaded: {target}")


def extract_zip(zip_path: Path, target_dir: Path, force: bool = False) -> Path:
    dataset_folder = target_dir / zip_path.stem
    if dataset_folder.exists() and not force:
        print(f"MovieLens folder exists: {dataset_folder}")
        return dataset_folder
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target_dir)
    print(f"Extracted: {dataset_folder}")
    return dataset_folder


def parse_title(title: str) -> tuple[str, int | None]:
    match = re.search(r"\((\d{4})\)\s*$", title)
    year = int(match.group(1)) if match else None
    clean = re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()
    return clean, year


def parse_genres(value: str) -> list[str]:
    if not isinstance(value, str) or not value or value == NO_GENRES:
        return []
    return [genre for genre in value.split("|") if genre]


def clean_movielens(dataset_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    movies = pd.read_csv(dataset_dir / "movies.csv")
    ratings = pd.read_csv(dataset_dir / "ratings.csv")
    tags = pd.read_csv(dataset_dir / "tags.csv")
    links = pd.read_csv(dataset_dir / "links.csv")

    movies = movies.rename(columns={"movieId": "movie_id"})
    parsed = movies["title"].map(parse_title)
    movies["title_clean"] = parsed.map(lambda item: item[0])
    movies["movie_year"] = parsed.map(lambda item: item[1]).astype("Int64")
    movies["genres_list"] = movies["genres"].map(parse_genres)
    movies["genres_json"] = movies["genres_list"].map(json_dumps)
    movies["genres_text"] = movies["genres_list"].map(lambda items: " ".join(items))

    ratings = ratings.rename(columns={"userId": "user_id", "movieId": "movie_id"})
    ratings["rated_at"] = pd.to_datetime(ratings["timestamp"], unit="s", utc=True).dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    tags = tags.rename(columns={"userId": "user_id", "movieId": "movie_id"})
    tags["tag"] = tags["tag"].fillna("").astype(str).str.strip()
    tags = tags[tags["tag"] != ""].copy()
    tags["tag_norm"] = tags["tag"].str.lower()
    tags["tagged_at"] = pd.to_datetime(tags["timestamp"], unit="s", utc=True).dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    links = links.rename(columns={"movieId": "movie_id", "imdbId": "imdb_id", "tmdbId": "tmdb_id"})
    links["tmdb_id"] = links["tmdb_id"].astype("Int64")
    links["imdb_id"] = links["imdb_id"].astype("Int64")
    links["imdb_tt_id"] = links["imdb_id"].map(lambda value: f"tt{int(value):07d}" if pd.notna(value) else None)

    movies.drop(columns=["genres_list"], errors="ignore").to_csv(INTERIM_DIR / "movies_clean.csv", index=False)
    ratings.to_csv(INTERIM_DIR / "ratings_clean.csv", index=False)
    tags.to_csv(INTERIM_DIR / "tags_clean.csv", index=False)
    links.to_csv(INTERIM_DIR / "links_clean.csv", index=False)
    return movies, ratings, tags, links


def aggregate_ratings(ratings: pd.DataFrame) -> pd.DataFrame:
    stats = (
        ratings.groupby("movie_id")["rating"]
        .agg(
            rating_count="count",
            rating_mean="mean",
            rating_median="median",
            rating_std="std",
            rating_min="min",
            rating_max="max",
        )
        .reset_index()
    )
    stats["rating_std"] = stats["rating_std"].fillna(0)
    return stats


def aggregate_tags(tags: pd.DataFrame) -> pd.DataFrame:
    if tags.empty:
        return pd.DataFrame(columns=["movie_id", "tag_count", "top_tags_json", "tags_text"])

    rows: list[dict[str, Any]] = []
    for movie_id, group in tags.groupby("movie_id"):
        counts = group["tag_norm"].value_counts()
        top_tags = counts.head(20).index.tolist()
        rows.append(
            {
                "movie_id": movie_id,
                "tag_count": int(len(group)),
                "top_tags_json": json_dumps(top_tags),
                "tags_text": " ".join(top_tags),
            }
        )
    return pd.DataFrame(rows)

