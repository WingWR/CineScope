from __future__ import annotations

import numpy as np
from scipy import sparse


class UserKnnRecommender:
    def __init__(self, knn_model, user_movie_matrix: sparse.csr_matrix, user_ids: list[int]) -> None:
        self.knn_model = knn_model
        self.user_movie_matrix = user_movie_matrix
        self.user_ids = user_ids

    def neighbor_user_indices(self, user_index: int, neighbor_k: int) -> tuple[np.ndarray, np.ndarray]:
        neighbor_count = min(neighbor_k + 1, len(self.user_ids))
        distances, indices = self.knn_model.kneighbors(
            self.user_movie_matrix[user_index],
            n_neighbors=neighbor_count,
        )
        kept_indices: list[int] = []
        kept_similarities: list[float] = []
        for distance, index in zip(distances.ravel(), indices.ravel()):
            if int(index) == int(user_index):
                continue
            similarity = max(0.0, 1.0 - float(distance))
            if similarity > 0 and np.isfinite(similarity):
                kept_indices.append(int(index))
                kept_similarities.append(similarity)
        return np.array(kept_indices, dtype=int), np.array(kept_similarities, dtype=np.float32)

    def personalized_scores(
        self,
        user_index: int,
        movie_ids: list[int],
        neighbor_k: int,
    ) -> dict[int, float]:
        neighbor_indices, similarities = self.neighbor_user_indices(user_index, neighbor_k)
        if len(neighbor_indices) == 0:
            return {}

        neighbor_matrix = self.user_movie_matrix[neighbor_indices].astype(np.float32)
        weighted_sum = np.asarray(neighbor_matrix.T.dot(similarities)).ravel()

        rated_mask = neighbor_matrix.copy()
        rated_mask.data = np.ones_like(rated_mask.data)
        denominator = np.asarray(rated_mask.T.dot(similarities)).ravel()

        with np.errstate(divide="ignore", invalid="ignore"):
            scores = np.divide(weighted_sum, denominator, out=np.zeros_like(weighted_sum), where=denominator > 0)

        current_rated = set(self.user_movie_matrix[user_index].indices.tolist())
        result: dict[int, float] = {}
        for movie_index, score in enumerate(scores):
            if movie_index in current_rated or denominator[movie_index] <= 0:
                continue
            if np.isfinite(score) and score > 0:
                result[int(movie_ids[movie_index])] = float(score)
        return result

