from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from scipy import sparse
from sklearn.neighbors import NearestNeighbors

from recommender.app.settings import COLLABORATIVE_ARTIFACT_DIR, MOVIES_FILE, RATINGS_FILE
from recommender.data.loaders import load_movies, load_ratings
from recommender.data.preprocess import normalize_title


def build_collaborative_artifacts(
    movies_path: str | Path = MOVIES_FILE,
    ratings_path: str | Path = RATINGS_FILE,
    output_dir: str | Path = COLLABORATIVE_ARTIFACT_DIR,
) -> dict[str, Any]:
    movies = load_movies(movies_path).reset_index(drop=True)
    ratings = load_ratings(ratings_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    movie_ids = movies["movie_id"].astype(int).tolist()
    user_ids = sorted(int(value) for value in ratings["user_id"].unique())
    movie_to_index = {movie_id: index for index, movie_id in enumerate(movie_ids)}
    user_to_index = {user_id: index for index, user_id in enumerate(user_ids)}

    valid_ratings = ratings[ratings["movie_id"].isin(movie_to_index)].copy()
    row_movie = valid_ratings["movie_id"].map(movie_to_index).to_numpy(dtype=int)
    col_user = valid_ratings["user_id"].map(user_to_index).to_numpy(dtype=int)
    values = valid_ratings["rating"].to_numpy(dtype=np.float32)

    movie_user_matrix = sparse.coo_matrix(
        (values, (row_movie, col_user)),
        shape=(len(movie_ids), len(user_ids)),
        dtype=np.float32,
    ).tocsr()
    user_movie_matrix = movie_user_matrix.T.tocsr()

    movie_knn = NearestNeighbors(metric="cosine", algorithm="brute")
    user_knn = NearestNeighbors(metric="cosine", algorithm="brute")
    movie_knn.fit(movie_user_matrix)
    user_knn.fit(user_movie_matrix)

    sparse.save_npz(output / "movie_user_matrix.npz", movie_user_matrix)
    sparse.save_npz(output / "user_movie_matrix.npz", user_movie_matrix)
    joblib.dump(movie_knn, output / "movie_knn.joblib")
    joblib.dump(user_knn, output / "user_knn.joblib")
    _write_json(output / "movie_index.json", _movie_index_payload(movies))
    _write_json(output / "user_index.json", _user_index_payload(user_ids))

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "movie_count": int(len(movie_ids)),
        "user_count": int(len(user_ids)),
        "rating_count": int(len(valid_ratings)),
        "movies_path": str(Path(movies_path).resolve()),
        "ratings_path": str(Path(ratings_path).resolve()),
    }
    _write_json(output / "metadata.json", metadata)
    return metadata


def _movie_index_payload(movies) -> dict[str, Any]:
    records = []
    for index, row in movies.iterrows():
        records.append(
            {
                "index": int(index),
                "movie_id": int(row["movie_id"]),
                "title": str(row.get("title_clean", "")),
                "normalized_title": normalize_title(row.get("title_clean", "")),
            }
        )
    return {"movies": records}


def _user_index_payload(user_ids: list[int]) -> dict[str, Any]:
    return {
        "users": [
            {"index": int(index), "user_id": int(user_id)}
            for index, user_id in enumerate(user_ids)
        ]
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

