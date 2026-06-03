from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.recommendations.recommender_client import RecommenderClient
from server.app.modules.recommendations.schemas import RecommendationRequest, RecommendationResponse


class RecommendationService:
    def __init__(self, recommender_client: RecommenderClient | None = None) -> None:
        self.recommender_client = recommender_client or RecommenderClient()

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        not_implemented("recommendations.service", "recommend")


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
