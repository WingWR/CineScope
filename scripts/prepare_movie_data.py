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
FINAL_DIR = DATA_DIR / "final"

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
    fallback_language: str
    bearer_token: str | None
    api_key: str | None


def ensure_dirs() -> None:
    for path in [
        RAW_DIR / "movielens",
        RAW_DIR / "tmdb",
        INTERIM_DIR,
        PROCESSED_DIR,
        FINAL_DIR,
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
        fallback_language=env.get("TMDB_FALLBACK_LANGUAGE", "en-US"),
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
            tmdb_id = record.get("_source_tmdb_id") or record.get("id")
            if tmdb_id is not None:
                cache[int(tmdb_id)] = record
    return cache


def tmdb_headers(config: TmdbConfig) -> dict[str, str]:
    headers = {"accept": "application/json"}
    if config.bearer_token:
        headers["Authorization"] = f"Bearer {config.bearer_token}"
    return headers


def image_language_param(language: str) -> str:
    if language == "en-US":
        return "en-US,en,null"
    if language.startswith("en"):
        return f"{language},en,null"
    return f"{language},en,null"


def parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return None


def choose_image_path(items: Any) -> str | None:
    if not isinstance(items, list) or not items:
        return None
    candidates = [item for item in items if isinstance(item, dict) and item.get("file_path")]
    if not candidates:
        return None
    best = max(
        candidates,
        key=lambda item: (
            item.get("vote_average") or 0,
            item.get("vote_count") or 0,
            item.get("width") or 0,
        ),
    )
    return best.get("file_path")


def fill_image_paths_from_append(record: dict[str, Any]) -> None:
    images = record.get("images") if isinstance(record.get("images"), dict) else {}
    if not record.get("poster_path"):
        record["poster_path"] = choose_image_path(images.get("posters"))
    if not record.get("backdrop_path"):
        record["backdrop_path"] = choose_image_path(images.get("backdrops"))


def record_title(record: dict[str, Any]) -> Any:
    return record.get("title") or record.get("name")


def record_original_title(record: dict[str, Any]) -> Any:
    return record.get("original_title") or record.get("original_name")


def record_release_date(record: dict[str, Any]) -> str:
    return record.get("release_date") or record.get("first_air_date") or ""


def record_runtime(record: dict[str, Any]) -> Any:
    runtime = record.get("runtime")
    if runtime:
        return runtime
    episode_run_time = record.get("episode_run_time")
    if isinstance(episode_run_time, list) and episode_run_time:
        return episode_run_time[0]
    return None


def needs_language_fallback(record: dict[str, Any]) -> bool:
    return any(
        [
            not record_title(record),
            not record.get("overview"),
            not record_release_date(record),
            not record_runtime(record),
            not record.get("poster_path"),
            not record.get("backdrop_path"),
        ]
    )


def merge_missing_tmdb_fields(primary: dict[str, Any], fallback: dict[str, Any], fallback_language: str) -> dict[str, Any]:
    merged = dict(primary)
    for field in [
        "title",
        "name",
        "overview",
        "release_date",
        "first_air_date",
        "runtime",
        "episode_run_time",
        "vote_average",
        "vote_count",
        "popularity",
        "original_language",
        "status",
        "poster_path",
        "backdrop_path",
        "genres",
    ]:
        if not merged.get(field) and fallback.get(field):
            merged[field] = fallback[field]
    if merged != primary:
        merged["_fallback_language_used"] = fallback_language
    return merged


def request_tmdb_detail(
    session: requests.Session,
    config: TmdbConfig,
    tmdb_id: int,
    language: str,
    sleep_seconds: float,
    media_type: str,
) -> dict[str, Any]:
    params = {
        "language": language,
        "append_to_response": "images",
        "include_image_language": image_language_param(language),
    }
    if not config.bearer_token and config.api_key:
        params["api_key"] = config.api_key
    url = f"{config.base_url}/{media_type}/{tmdb_id}"
    last_error: requests.RequestException | None = None
    for attempt in range(1, 6):
        response = session.get(url, params=params, headers=tmdb_headers(config), timeout=30)
        if response.status_code == 429:
            retry_after = parse_retry_after(response.headers.get("Retry-After"))
            wait_seconds = retry_after if retry_after is not None else max(sleep_seconds * attempt * 4, 1.0)
            print(f"TMDb 429 for {tmdb_id}; sleeping {wait_seconds:.1f}s before retry")
            time.sleep(wait_seconds)
            continue
        if response.status_code in {500, 502, 503, 504}:
            time.sleep(max(sleep_seconds * attempt * 4, 1.0))
            continue
        try:
            response.raise_for_status()
        except requests.RequestException as error:
            last_error = error
            break
        record = response.json()
        record["_requested_language"] = language
        record["_tmdb_media_type"] = media_type
        record["_source_tmdb_id"] = tmdb_id
        record["_resolved_tmdb_id"] = record.get("id")
        fill_image_paths_from_append(record)
        return record
    if last_error is not None:
        raise last_error
    response.raise_for_status()
    raise RuntimeError(f"TMDb request failed for {tmdb_id}")


def request_tmdb_find(
    session: requests.Session,
    config: TmdbConfig,
    imdb_tt_id: str,
    sleep_seconds: float,
) -> tuple[str, int] | None:
    params = {"external_source": "imdb_id"}
    if not config.bearer_token and config.api_key:
        params["api_key"] = config.api_key
    url = f"{config.base_url}/find/{imdb_tt_id}"
    for attempt in range(1, 6):
        response = session.get(url, params=params, headers=tmdb_headers(config), timeout=30)
        if response.status_code == 429:
            retry_after = parse_retry_after(response.headers.get("Retry-After"))
            wait_seconds = retry_after if retry_after is not None else max(sleep_seconds * attempt * 4, 1.0)
            print(f"TMDb 429 for find/{imdb_tt_id}; sleeping {wait_seconds:.1f}s before retry")
            time.sleep(wait_seconds)
            continue
        if response.status_code in {500, 502, 503, 504}:
            time.sleep(max(sleep_seconds * attempt * 4, 1.0))
            continue
        response.raise_for_status()
        payload = response.json()
        for media_type, key in [("movie", "movie_results"), ("tv", "tv_results")]:
            results = payload.get(key)
            if isinstance(results, list) and results:
                resolved_id = results[0].get("id")
                if resolved_id is not None:
                    return media_type, int(resolved_id)
        return None
    response.raise_for_status()
    return None


def fetch_one_tmdb(
    session: requests.Session,
    config: TmdbConfig,
    tmdb_id: int,
    sleep_seconds: float,
    imdb_tt_id: str | None = None,
) -> dict[str, Any]:
    media_type = "movie"
    try:
        record = request_tmdb_detail(
            session=session,
            config=config,
            tmdb_id=tmdb_id,
            language=config.language,
            sleep_seconds=sleep_seconds,
            media_type=media_type,
        )
    except requests.HTTPError as error:
        status = error.response.status_code if error.response is not None else None
        if status != 404:
            raise
        media_type = "tv"
        try:
            record = request_tmdb_detail(
                session=session,
                config=config,
                tmdb_id=tmdb_id,
                language=config.language,
                sleep_seconds=sleep_seconds,
                media_type=media_type,
            )
        except requests.HTTPError as tv_error:
            tv_status = tv_error.response.status_code if tv_error.response is not None else None
            if tv_status != 404 or not imdb_tt_id:
                raise
            resolved = request_tmdb_find(session, config, imdb_tt_id, sleep_seconds)
            if resolved is None:
                raise tv_error
            media_type, resolved_id = resolved
            record = request_tmdb_detail(
                session=session,
                config=config,
                tmdb_id=resolved_id,
                language=config.language,
                sleep_seconds=sleep_seconds,
                media_type=media_type,
            )
            record["_source_tmdb_id"] = tmdb_id
            record["_resolved_tmdb_id"] = resolved_id
            record["_resolved_from_imdb_id"] = imdb_tt_id
    if config.fallback_language != config.language and needs_language_fallback(record):
        try:
            fallback = request_tmdb_detail(
                session=session,
                config=config,
                tmdb_id=tmdb_id,
                language=config.fallback_language,
                sleep_seconds=sleep_seconds,
                media_type=media_type,
            )
            record = merge_missing_tmdb_fields(record, fallback, config.fallback_language)
        except requests.HTTPError as error:
            status = error.response.status_code if error.response is not None else None
            if status not in {404}:
                raise
    return record


def fetch_tmdb_details(
    tmdb_ids: list[int],
    external_id_by_tmdb_id: dict[int, str],
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
    failures: dict[int, dict[str, Any]] = {}
    with requests.Session() as session, cache_path.open("a", encoding="utf-8") as cache_fh:
        for index, tmdb_id in enumerate(missing, start=1):
            last_error = ""
            for attempt in range(1, 4):
                try:
                    record = fetch_one_tmdb(
                        session,
                        config,
                        tmdb_id,
                        sleep_seconds=sleep_seconds,
                        imdb_tt_id=external_id_by_tmdb_id.get(tmdb_id),
                    )
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
            if tmdb_id not in cache:
                failures[tmdb_id] = {"tmdb_id": tmdb_id, "error": last_error or "not_found"}

            if index % 50 == 0 or index == len(missing):
                print(f"TMDb progress: {index}/{len(missing)}")
            time.sleep(sleep_seconds)

    if failures:
        with failures_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["tmdb_id", "error"])
            writer.writeheader()
            writer.writerows(failures.values())
    return cache


def tmdb_image_url(config: TmdbConfig, path: Any, size: str) -> str | None:
    if not isinstance(path, str) or not path:
        return None
    return f"{config.image_base_url}/{size}{path}"


def tmdb_cache_to_frame(cache: dict[int, dict[str, Any]], config: TmdbConfig) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tmdb_id, record in cache.items():
        release_date = record_release_date(record)
        tmdb_year = int(release_date[:4]) if re.match(r"^\d{4}", release_date) else None
        rows.append(
            {
                "tmdb_id": tmdb_id,
                "tmdb_resolved_id": record.get("_resolved_tmdb_id") or record.get("id") or tmdb_id,
                "tmdb_resolved_from_imdb_id": record.get("_resolved_from_imdb_id"),
                "tmdb_media_type": record.get("_tmdb_media_type", "movie"),
                "tmdb_title": record_title(record),
                "tmdb_original_title": record_original_title(record),
                "overview": record.get("overview"),
                "release_date": release_date or None,
                "tmdb_year": tmdb_year,
                "runtime_minutes": record_runtime(record),
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
    final_features = features[features["movie_id"].isin(final_movie_ids)].copy()

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

    final_movies.to_csv(FINAL_DIR / "movies.csv", index=False)
    final_ratings.to_csv(FINAL_DIR / "ratings.csv", index=False)
    final_tags.to_csv(FINAL_DIR / "tags.csv", index=False)
    final_features.to_csv(FINAL_DIR / "movie_features.csv", index=False)
    final_genre_stats.to_csv(FINAL_DIR / "genre_stats.csv", index=False)

    def missing_or_blank_count(frame: pd.DataFrame, column: str) -> int:
        values = frame[column]
        blank_count = values.astype("string").str.strip().eq("").fillna(False).sum()
        return int(values.isna().sum() + blank_count)

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
        "display_title_missing_count": missing_or_blank_count(final_movies, "display_title"),
        "display_year_missing_count": int(final_movies["display_year"].isna().sum()),
        "overview_missing_count": missing_or_blank_count(final_movies, "overview"),
        "runtime_minutes_missing_count": int(final_movies["runtime_minutes"].isna().sum()),
        "poster_url_missing_count": missing_or_blank_count(final_movies, "poster_url"),
        "backdrop_url_missing_count": missing_or_blank_count(final_movies, "backdrop_url"),
        "search_text_missing_count": missing_or_blank_count(final_movies, "search_text"),
        "feature_text_missing_count": missing_or_blank_count(final_features, "feature_text"),
    }

    (FINAL_DIR / "dataset_summary.json").write_text(json_dumps(summary), encoding="utf-8")
    (FINAL_DIR / "quality_report.json").write_text(json_dumps(quality_report), encoding="utf-8")
    return quality_report


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
    final_quality_report = write_final_outputs(
        enriched=enriched,
        ratings=ratings,
        tags=tags,
        features=features,
        genre_frame=genre_frame,
        dataset_name="ml-latest-small",
    )

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
        "final_movie_count": final_quality_report["source_movie_with_tmdb_detail_count"],
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
    external_id_by_tmdb_id = {
        int(row.tmdb_id): row.imdb_tt_id
        for row in links[links["tmdb_id"].notna() & links["imdb_tt_id"].notna()].itertuples()
    }
    if args.fetch_tmdb:
        tmdb_cache = fetch_tmdb_details(
            tmdb_ids=tmdb_ids,
            external_id_by_tmdb_id=external_id_by_tmdb_id,
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
