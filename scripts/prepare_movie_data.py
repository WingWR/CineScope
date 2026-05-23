from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

MOVIELENS_DATASETS = {
    "ml-latest-small": {
        "url": "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
        "folder": "ml-latest-small",
    }
}

NO_GENRES = "(no genres listed)"


@dataclass(frozen=True)
class TmdbConfig:
    base_url: str
    image_base_url: str
    language: str
    bearer_token: str | None
    api_key: str | None


def ensure_dirs() -> None:
    for path in [
        RAW_DIR / "movielens",
        RAW_DIR / "tmdb",
        INTERIM_DIR,
        PROCESSED_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_tmdb_config() -> TmdbConfig:
    env = {}
    env.update(load_env_file(ROOT / ".env"))
    env.update(load_env_file(DATA_DIR / ".env"))
    env.update(os.environ)
    return TmdbConfig(
        base_url=env.get("TMDB_BASE_URL", "https://api.themoviedb.org/3").rstrip("/"),
        image_base_url=env.get("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p").rstrip("/"),
        language=env.get("TMDB_DEFAULT_LANGUAGE", "zh-CN"),
        bearer_token=env.get("TMDB_BEARER_TOKEN") or None,
        api_key=env.get("TMDB_API_KEY") or None,
    )


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


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


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


def load_tmdb_cache(cache_path: Path) -> dict[int, dict[str, Any]]:
    cache: dict[int, dict[str, Any]] = {}
    if not cache_path.exists():
        return cache
    with cache_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            record = json.loads(line)
            tmdb_id = record.get("id")
            if tmdb_id is not None:
                cache[int(tmdb_id)] = record
    return cache


def tmdb_headers(config: TmdbConfig) -> dict[str, str]:
    headers = {"accept": "application/json"}
    if config.bearer_token:
        headers["Authorization"] = f"Bearer {config.bearer_token}"
    return headers


def fetch_one_tmdb(session: requests.Session, config: TmdbConfig, tmdb_id: int) -> dict[str, Any]:
    params = {"language": config.language}
    if not config.bearer_token and config.api_key:
        params["api_key"] = config.api_key
    url = f"{config.base_url}/movie/{tmdb_id}"
    response = session.get(url, params=params, headers=tmdb_headers(config), timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_tmdb_details(
    tmdb_ids: list[int],
    config: TmdbConfig,
    cache_path: Path,
    failures_path: Path,
    limit: int | None,
    sleep_seconds: float,
    allow_full: bool,
) -> dict[int, dict[str, Any]]:
    if not config.bearer_token and not config.api_key:
        raise RuntimeError("TMDb credentials missing. Set TMDB_BEARER_TOKEN or TMDB_API_KEY in environment/data/.env.")

    cache = load_tmdb_cache(cache_path)
    missing = [tmdb_id for tmdb_id in tmdb_ids if tmdb_id not in cache]
    if limit is not None:
        missing = missing[:limit]
    elif len(missing) > 500 and not allow_full:
        raise RuntimeError(
            f"Refusing to fetch {len(missing)} TMDb records without --allow-full-tmdb. "
            "Use --tmdb-limit for a sample run."
        )

    if not missing:
        print("TMDb cache is already complete for requested scope.")
        return cache

    print(f"Fetching TMDb details: {len(missing)} missing records")
    failures: list[dict[str, Any]] = []
    with requests.Session() as session, cache_path.open("a", encoding="utf-8") as cache_fh:
        for index, tmdb_id in enumerate(missing, start=1):
            last_error = ""
            for attempt in range(1, 4):
                try:
                    record = fetch_one_tmdb(session, config, tmdb_id)
                    cache[int(tmdb_id)] = record
                    cache_fh.write(json_dumps(record) + "\n")
                    cache_fh.flush()
                    break
                except requests.HTTPError as error:
                    status = error.response.status_code if error.response is not None else None
                    last_error = f"HTTP {status}"
                    if status == 404:
                        break
                    time.sleep(sleep_seconds * attempt)
                except requests.RequestException as error:
                    last_error = type(error).__name__
                    time.sleep(sleep_seconds * attempt)
            else:
                failures.append({"tmdb_id": tmdb_id, "error": last_error})

            if tmdb_id not in cache:
                failures.append({"tmdb_id": tmdb_id, "error": last_error or "not_found"})

            if index % 50 == 0 or index == len(missing):
                print(f"TMDb progress: {index}/{len(missing)}")
            time.sleep(sleep_seconds)

    if failures:
        with failures_path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["tmdb_id", "error"])
            if failures_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerows(failures)
    return cache


def tmdb_image_url(config: TmdbConfig, path: Any, size: str) -> str | None:
    if not isinstance(path, str) or not path:
        return None
    return f"{config.image_base_url}/{size}{path}"


def tmdb_cache_to_frame(cache: dict[int, dict[str, Any]], config: TmdbConfig) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tmdb_id, record in cache.items():
        release_date = record.get("release_date") or ""
        tmdb_year = int(release_date[:4]) if re.match(r"^\d{4}", release_date) else None
        rows.append(
            {
                "tmdb_id": tmdb_id,
                "tmdb_title": record.get("title"),
                "tmdb_original_title": record.get("original_title"),
                "overview": record.get("overview"),
                "release_date": release_date or None,
                "tmdb_year": tmdb_year,
                "runtime_minutes": record.get("runtime"),
                "tmdb_vote_average": record.get("vote_average"),
                "tmdb_vote_count": record.get("vote_count"),
                "tmdb_popularity": record.get("popularity"),
                "original_language": record.get("original_language"),
                "tmdb_status": record.get("status"),
                "poster_path": record.get("poster_path"),
                "poster_url": tmdb_image_url(config, record.get("poster_path"), "w500"),
                "backdrop_path": record.get("backdrop_path"),
                "backdrop_url": tmdb_image_url(config, record.get("backdrop_path"), "w780"),
                "tmdb_genres_json": json_dumps([item.get("name") for item in record.get("genres", []) if item.get("name")]),
            }
        )
    return pd.DataFrame(rows)


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

    summary = {
        "dataset": "ml-latest-small",
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
    }
    (PROCESSED_DIR / "dataset_summary.json").write_text(json_dumps(summary), encoding="utf-8")
    print(f"Wrote processed files to {PROCESSED_DIR}")


def prepare(args: argparse.Namespace) -> None:
    ensure_dirs()
    dataset = MOVIELENS_DATASETS[args.dataset]
    zip_path = RAW_DIR / "movielens" / f"{args.dataset}.zip"
    download_file(dataset["url"], zip_path, force=args.force_download)
    dataset_dir = extract_zip(zip_path, RAW_DIR / "movielens", force=args.force_extract)

    movies, ratings, tags, links = clean_movielens(dataset_dir)
    config = load_tmdb_config()
    tmdb_cache_path = RAW_DIR / "tmdb" / "movie_details.jsonl"
    tmdb_failures_path = RAW_DIR / "tmdb" / "movie_failures.csv"

    tmdb_ids = sorted({int(value) for value in links["tmdb_id"].dropna().tolist()})
    if args.fetch_tmdb:
        tmdb_cache = fetch_tmdb_details(
            tmdb_ids=tmdb_ids,
            config=config,
            cache_path=tmdb_cache_path,
            failures_path=tmdb_failures_path,
            limit=args.tmdb_limit,
            sleep_seconds=args.tmdb_sleep,
            allow_full=args.allow_full_tmdb,
        )
    else:
        tmdb_cache = load_tmdb_cache(tmdb_cache_path)
        print(f"TMDb fetch disabled. Loaded cached records: {len(tmdb_cache)}")

    build_outputs(movies, ratings, tags, links, tmdb_cache, config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare CineScope MovieLens + TMDb data assets.")
    parser.add_argument("--dataset", choices=sorted(MOVIELENS_DATASETS), default="ml-latest-small")
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--force-extract", action="store_true")
    parser.add_argument("--fetch-tmdb", action="store_true", help="Fetch TMDb details for missing tmdbId records.")
    parser.add_argument("--tmdb-limit", type=int, default=None, help="Limit TMDb requests for validation runs.")
    parser.add_argument("--tmdb-sleep", type=float, default=0.25, help="Sleep seconds between TMDb requests.")
    parser.add_argument(
        "--allow-full-tmdb",
        action="store_true",
        help="Allow fetching all missing TMDb records. This may issue thousands of requests.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    prepare(parse_args())
