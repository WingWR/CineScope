from __future__ import annotations

from server.app.core.config import get_config
from server.app.core.errors import not_implemented


class RecommenderClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or get_config().recommender_base_url

    def recommend_content(self, movie_name: str, top_k: int):
        not_implemented("recommendations.recommender_client", "recommend_content")

    def recommend_collaborative(
        self,
        user_id: int,
        movie_name: str | None,
        top_k: int,
    ):
        not_implemented("recommendations.recommender_client", "recommend_collaborative")
