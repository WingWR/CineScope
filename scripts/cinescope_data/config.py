from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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

