from __future__ import annotations

import argparse
from dataclasses import dataclass

import pandas as pd

from .config import MOVIELENS_DATASETS, RAW_DIR, TmdbConfig, ensure_dirs, load_tmdb_config
from .movielens import clean_movielens, download_file, extract_zip
from .submission import rewrite_existing_final_for_submission
from .tmdb_client import fetch_tmdb_details, load_tmdb_cache
from .transform import build_outputs


@dataclass(frozen=True)
class PipelineOptions:
    dataset: str
    force_download: bool
    force_extract: bool
    fetch_tmdb: bool
    tmdb_limit: int | None
    tmdb_sleep: float
    allow_full_tmdb: bool
    submission_only: bool

    @classmethod
    def from_namespace(cls, args: argparse.Namespace) -> "PipelineOptions":
        return cls(
            dataset=args.dataset,
            force_download=args.force_download,
            force_extract=args.force_extract,
            fetch_tmdb=args.fetch_tmdb,
            tmdb_limit=args.tmdb_limit,
            tmdb_sleep=args.tmdb_sleep,
            allow_full_tmdb=args.allow_full_tmdb,
            submission_only=args.submission_only,
        )


class CineScopeDataPipeline:
    def __init__(self, options: PipelineOptions) -> None:
        self.options = options

    def run(self) -> None:
        ensure_dirs()
        if self.options.submission_only:
            rewrite_existing_final_for_submission()
            print("Rewrote data/final files for RQ.md submission scope")
            return

        dataset_dir = self.prepare_movielens_archive()
        movies, ratings, tags, links = clean_movielens(dataset_dir)
        config = load_tmdb_config()
        tmdb_cache = self.load_tmdb_records(config, links)
        build_outputs(
            movies=movies,
            ratings=ratings,
            tags=tags,
            links=links,
            tmdb_cache=tmdb_cache,
            config=config,
            dataset_name=self.options.dataset,
        )

    def prepare_movielens_archive(self):
        dataset = MOVIELENS_DATASETS[self.options.dataset]
        zip_path = RAW_DIR / "movielens" / f"{self.options.dataset}.zip"
        download_file(dataset["url"], zip_path, force=self.options.force_download)
        return extract_zip(zip_path, RAW_DIR / "movielens", force=self.options.force_extract)

    def load_tmdb_records(
        self,
        config: TmdbConfig,
        links: pd.DataFrame,
    ) -> dict[int, dict]:
        tmdb_cache_path = RAW_DIR / "tmdb" / "movie_details.jsonl"
        tmdb_failures_path = RAW_DIR / "tmdb" / "movie_failures.csv"

        tmdb_ids = sorted({int(value) for value in links["tmdb_id"].dropna().tolist()})
        external_id_by_tmdb_id = {
            int(row.tmdb_id): row.imdb_tt_id
            for row in links[links["tmdb_id"].notna() & links["imdb_tt_id"].notna()].itertuples()
        }
        if self.options.fetch_tmdb:
            return fetch_tmdb_details(
                tmdb_ids=tmdb_ids,
                external_id_by_tmdb_id=external_id_by_tmdb_id,
                config=config,
                cache_path=tmdb_cache_path,
                failures_path=tmdb_failures_path,
                limit=self.options.tmdb_limit,
                sleep_seconds=self.options.tmdb_sleep,
                allow_full=self.options.allow_full_tmdb,
            )

        tmdb_cache = load_tmdb_cache(tmdb_cache_path)
        print(f"TMDb fetch disabled. Loaded cached records: {len(tmdb_cache)}")
        return tmdb_cache


def prepare(args: argparse.Namespace) -> None:
    CineScopeDataPipeline(PipelineOptions.from_namespace(args)).run()
