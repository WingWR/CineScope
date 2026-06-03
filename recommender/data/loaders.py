from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_movies(path: str | Path) -> pd.DataFrame:
    movies = pd.read_csv(path)
    movies["movie_id"] = pd.to_numeric(movies["movie_id"], errors="coerce").astype("Int64")
    return movies[movies["movie_id"].notna()].copy()


def load_ratings(path: str | Path) -> pd.DataFrame:
    ratings = pd.read_csv(path)
    ratings["user_id"] = pd.to_numeric(ratings["user_id"], errors="coerce").astype("Int64")
    ratings["movie_id"] = pd.to_numeric(ratings["movie_id"], errors="coerce").astype("Int64")
    ratings["rating"] = pd.to_numeric(ratings["rating"], errors="coerce")
    ratings = ratings.dropna(subset=["user_id", "movie_id", "rating"])
    ratings["user_id"] = ratings["user_id"].astype(int)
    ratings["movie_id"] = ratings["movie_id"].astype(int)
    return ratings

