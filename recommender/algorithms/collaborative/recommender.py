from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from scipy import sparse

from recommender.algorithms.collaborative.item_knn import ItemKnnRecommender
from recommender.algorithms.collaborative.user_knn import UserKnnRecommender
from recommender.app.settings import COLLABORATIVE_ARTIFACT_DIR
from recommender.core.exceptions import ArtifactsMissingError, UserNotFoundError
from recommender.core.ranking import merge_weighted_scores, top_scores
from recommender.data.preprocess import find_movie_index


class CollaborativeRecommender:
    def __init__(
        self,
        movies: pd.DataFrame,
        ratings: pd.DataFrame,
        artifact_dir: str | Path = COLLABORATIVE_ARTIFACT_DIR,
        item_weight: float = 0.4,
        user_weight: float = 0.6,
    ) -> None:
        self.movies = movies.reset_index(drop=True)
        self.ratings = ratings
        self.artifact_dir = Path(artifact_dir)
        self.item_weight = item_weight
        self.user_weight = user_weight
        self._load_artifacts()

    def recommend(
        self,
        user_id: int,
        movie_name: str | None = None,
        top_k: int = 10,
        neighbor_k: int = 10,
    ) -> list[tuple[int, float, str, str]]:
        user_id = int(user_id)
        if user_id not in self.user_to_index:
            raise UserNotFoundError(f"User not found: {user_id}")

        user_index = self.user_to_index[user_id]
        seen_movie_ids = self._seen_movies(user_index)
        score_groups: list[tuple[dict[int, float], float]] = []
        input_movie_id: int | None = None

        if movie_name:
            movie_index = find_movie_index(self.movies, movie_name)
            input_movie_id = int(self.movies.iloc[movie_index]["movie_id"])
            item_scores = self.item_recommender.similar_movies(movie_index, candidate_k=max(top_k * 8, 50))
            score_groups.append((item_scores, self.item_weight))

        user_scores = self.user_recommender.personalized_scores(
            user_index=user_index,
            movie_ids=self.movie_ids,
            neighbor_k=neighbor_k,
        )
        score_groups.append((user_scores, self.user_weight if movie_name else 1.0))

        excluded = set(seen_movie_ids)
        if input_movie_id is not None:
            excluded.add(input_movie_id)

        combined = merge_weighted_scores(score_groups, exclude=excluded)
        combined = self._fill_with_popular(combined, excluded, top_k)

        reason = (
            "item KNN movie similarity + user KNN personalized neighbors"
            if movie_name
            else "user KNN personalized neighbors"
        )
        return [
            (candidate_id, score, reason, "collaborative")
            for candidate_id, score in top_scores(combined, top_k)
        ]

    def _seen_movies(self, user_index: int) -> set[int]:
        movie_indices = self.user_movie_matrix[user_index].indices.tolist()
        return {int(self.movie_ids[index]) for index in movie_indices}

    def _fill_with_popular(
        self,
        scores: dict[int, float],
        excluded: set[int],
        top_k: int,
    ) -> dict[int, float]:
        if len(scores) >= top_k:
            return scores

        result = dict(scores)
        candidates = self.movies.copy()
        candidates["rating_count"] = pd.to_numeric(candidates.get("rating_count"), errors="coerce").fillna(0)
        candidates["rating_mean"] = pd.to_numeric(candidates.get("rating_mean"), errors="coerce").fillna(0)
        global_mean = float(candidates["rating_mean"].mean())
        min_votes = max(10.0, float(candidates["rating_count"].quantile(0.75)))
        candidates["bayesian_score"] = (
            (candidates["rating_count"] / (candidates["rating_count"] + min_votes)) * candidates["rating_mean"]
            + (min_votes / (candidates["rating_count"] + min_votes)) * global_mean
        )
        candidates = candidates.sort_values("bayesian_score", ascending=False)

        fallback_score = 0.001
        for _, row in candidates.iterrows():
            movie_id = int(row["movie_id"])
            if movie_id in excluded or movie_id in result:
                continue
            result[movie_id] = fallback_score
            fallback_score *= 0.99
            if len(result) >= top_k:
                break
        return result

    def _load_artifacts(self) -> None:
        required = [
            self.artifact_dir / "movie_user_matrix.npz",
            self.artifact_dir / "user_movie_matrix.npz",
            self.artifact_dir / "movie_knn.joblib",
            self.artifact_dir / "user_knn.joblib",
            self.artifact_dir / "movie_index.json",
            self.artifact_dir / "user_index.json",
        ]
        missing = [path for path in required if not path.exists()]
        if missing:
            raise ArtifactsMissingError(
                "Collaborative artifacts are missing. Run: python -m recommender.scripts.build_collaborative_artifacts"
            )

        self.movie_user_matrix = sparse.load_npz(self.artifact_dir / "movie_user_matrix.npz").tocsr()
        self.user_movie_matrix = sparse.load_npz(self.artifact_dir / "user_movie_matrix.npz").tocsr()
        self.movie_knn = joblib.load(self.artifact_dir / "movie_knn.joblib")
        self.user_knn = joblib.load(self.artifact_dir / "user_knn.joblib")
        self.movie_ids = _load_movie_ids(self.artifact_dir / "movie_index.json")
        self.user_ids = _load_user_ids(self.artifact_dir / "user_index.json")
        self.user_to_index = {user_id: index for index, user_id in enumerate(self.user_ids)}
        self.item_recommender = ItemKnnRecommender(self.movie_knn, self.movie_user_matrix, self.movie_ids)
        self.user_recommender = UserKnnRecommender(self.user_knn, self.user_movie_matrix, self.user_ids)


def _load_movie_ids(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [int(record["movie_id"]) for record in payload["movies"]]


def _load_user_ids(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [int(record["user_id"]) for record in payload["users"]]

