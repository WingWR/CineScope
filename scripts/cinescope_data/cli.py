from __future__ import annotations

import argparse

from .config import MOVIELENS_DATASETS
from .pipeline import prepare


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


def main() -> None:
    prepare(parse_args())

