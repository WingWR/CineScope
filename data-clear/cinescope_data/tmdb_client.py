from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .config import TmdbConfig
from .utils import json_dumps


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
    detail_tmdb_id = tmdb_id
    try:
        record = request_tmdb_detail(
            session=session,
            config=config,
            tmdb_id=detail_tmdb_id,
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
                tmdb_id=detail_tmdb_id,
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
            media_type, detail_tmdb_id = resolved
            record = request_tmdb_detail(
                session=session,
                config=config,
                tmdb_id=detail_tmdb_id,
                language=config.language,
                sleep_seconds=sleep_seconds,
                media_type=media_type,
            )
            record["_source_tmdb_id"] = tmdb_id
            record["_resolved_tmdb_id"] = detail_tmdb_id
            record["_resolved_from_imdb_id"] = imdb_tt_id
    if config.fallback_language != config.language and needs_language_fallback(record):
        try:
            fallback = request_tmdb_detail(
                session=session,
                config=config,
                tmdb_id=detail_tmdb_id,
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
                "tmdb_genres_json": json_dumps(
                    [item.get("name") for item in record.get("genres", []) if item.get("name")]
                ),
            }
        )
    return pd.DataFrame(rows)

