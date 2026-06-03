from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
FINAL_DATA_DIR = ROOT_DIR / "data" / "final"


def load_movies(path: str | Path | None = None) -> pd.DataFrame:
    """Load the final movie table used by training and inference."""
    data_path = Path(path) if path else FINAL_DATA_DIR / "movies.csv"
    return pd.read_csv(data_path)


def load_ratings(path: str | Path | None = None) -> pd.DataFrame:
    data_path = Path(path) if path else FINAL_DATA_DIR / "ratings.csv"
    return pd.read_csv(data_path)


def load_tags(path: str | Path | None = None) -> pd.DataFrame:
    data_path = Path(path) if path else FINAL_DATA_DIR / "tags.csv"
    return pd.read_csv(data_path)
