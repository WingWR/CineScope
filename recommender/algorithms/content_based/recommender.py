from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

from recommender.app.settings import CONTENT_ARTIFACT_DIR
from recommender.core.exceptions import ArtifactsMissingError
from recommender.core.ranking import merge_weighted_scores, top_scores
from recommender.data.preprocess import find_movie_index


class ContentBasedRecommender:
    def __init__(
        self,
        movies: pd.DataFrame,
        artifact_dir: str | Path = CONTENT_ARTIFACT_DIR,
        overview_weight: float = 0.55,
        content_weight: float = 0.45,
    ) -> None:
        self.movies = movies.reset_index(drop=True)
        self.artifact_dir = Path(artifact_dir)
        self.overview_weight = overview_weight
        self.content_weight = content_weight
        self._load_artifacts()

    def recommend(self, movie_name: str, top_k: int = 10) -> list[tuple[int, float, str, str]]:
        movie_index = find_movie_index(self.movies, movie_name)
        movie_id = int(self.movies.iloc[movie_index]["movie_id"])

        overview_scores = self._similarity_scores(self.overview_matrix, movie_index)
        content_scores = self._similarity_scores(self.content_matrix, movie_index)

        combined = merge_weighted_scores(
            [
                (overview_scores, self.overview_weight),
                (content_scores, self.content_weight),
            ],
            exclude={movie_id},
        )
        return [
            (
                candidate_id,
                score,
                "overview TF-IDF + content CountVectorizer similarity",
                "content_based",
            )
            for candidate_id, score in top_scores(combined, top_k)
        ]

    def _similarity_scores(self, matrix: sparse.csr_matrix, movie_index: int) -> dict[int, float]:
        similarities = cosine_similarity(matrix[movie_index], matrix).ravel()
        scores: dict[int, float] = {}
        for index, score in enumerate(similarities):
            movie_id = int(self.movies.iloc[index]["movie_id"])
            if index == movie_index or not np.isfinite(score):
                continue
            scores[movie_id] = float(score)
        return scores

    def _load_artifacts(self) -> None:
        required = [
            self.artifact_dir / "overview_tfidf.joblib",
            self.artifact_dir / "content_count.joblib",
            self.artifact_dir / "overview_matrix.npz",
            self.artifact_dir / "content_matrix.npz",
        ]
        missing = [path for path in required if not path.exists()]
        if missing:
            raise ArtifactsMissingError(
                "Content artifacts are missing. Run: python -m recommender.scripts.build_content_artifacts"
            )
        self.overview_vectorizer = joblib.load(self.artifact_dir / "overview_tfidf.joblib")
        self.content_vectorizer = joblib.load(self.artifact_dir / "content_count.joblib")
        self.overview_matrix = sparse.load_npz(self.artifact_dir / "overview_matrix.npz").tocsr()
        self.content_matrix = sparse.load_npz(self.artifact_dir / "content_matrix.npz").tocsr()

