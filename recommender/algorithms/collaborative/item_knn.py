from __future__ import annotations

import numpy as np
from scipy import sparse


class ItemKnnRecommender:
    def __init__(self, knn_model, movie_user_matrix: sparse.csr_matrix, movie_ids: list[int]) -> None:
        self.knn_model = knn_model
        self.movie_user_matrix = movie_user_matrix
        self.movie_ids = movie_ids

    def similar_movies(self, movie_index: int, candidate_k: int) -> dict[int, float]:
        neighbor_count = min(candidate_k + 1, len(self.movie_ids))
        distances, indices = self.knn_model.kneighbors(
            self.movie_user_matrix[movie_index],
            n_neighbors=neighbor_count,
        )
        scores: dict[int, float] = {}
        for distance, index in zip(distances.ravel(), indices.ravel()):
            if int(index) == int(movie_index):
                continue
            similarity = 1.0 - float(distance)
            if np.isfinite(similarity):
                scores[int(self.movie_ids[int(index)])] = max(0.0, similarity)
        return scores

