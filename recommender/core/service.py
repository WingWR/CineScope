from __future__ import annotations

from recommender.algorithms.collaborative.recommender import CollaborativeRecommender
from recommender.algorithms.content_based.recommender import ContentBasedRecommender
from recommender.app.schemas import RecommendationItem, RecommendationResponse
from recommender.app.settings import (
    COLLABORATIVE_ARTIFACT_DIR,
    CONTENT_ARTIFACT_DIR,
    DEFAULT_NEIGHBOR_K,
    DEFAULT_TOP_K,
    MOVIES_FILE,
    RATINGS_FILE,
)
from recommender.data.loaders import load_movies, load_ratings
from recommender.data.preprocess import movie_to_item


class RecommenderService:
    def __init__(self) -> None:
        self.movies = load_movies(MOVIES_FILE)
        self.ratings = load_ratings(RATINGS_FILE)
        self.content_recommender = ContentBasedRecommender(
            movies=self.movies,
            artifact_dir=CONTENT_ARTIFACT_DIR,
        )
        self.collaborative_recommender = CollaborativeRecommender(
            movies=self.movies,
            ratings=self.ratings,
            artifact_dir=COLLABORATIVE_ARTIFACT_DIR,
        )

    def recommend_by_content(
        self,
        movie_name: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> RecommendationResponse:
        recommendations = self.content_recommender.recommend(movie_name, top_k)
        items = [
            RecommendationItem(**movie_to_item(self.movies, movie_id, score, reason, source))
            for movie_id, score, reason, source in recommendations
        ]
        return RecommendationResponse(
            query={"movie_name": movie_name, "method": "content_based"},
            count=len(items),
            items=items,
        )

    def recommend_by_collaborative(
        self,
        user_id: int,
        movie_name: str | None = None,
        top_k: int = DEFAULT_TOP_K,
        neighbor_k: int = DEFAULT_NEIGHBOR_K,
    ) -> RecommendationResponse:
        recommendations = self.collaborative_recommender.recommend(
            user_id=user_id,
            movie_name=movie_name,
            top_k=top_k,
            neighbor_k=neighbor_k,
        )
        items = [
            RecommendationItem(**movie_to_item(self.movies, movie_id, score, reason, source))
            for movie_id, score, reason, source in recommendations
        ]
        return RecommendationResponse(
            query={
                "user_id": user_id,
                "movie_name": movie_name,
                "method": "collaborative",
                "neighbor_k": neighbor_k,
            },
            count=len(items),
            items=items,
        )

