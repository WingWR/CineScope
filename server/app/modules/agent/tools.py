from __future__ import annotations

from ...modules.movies.schemas import MovieListResponse
from ...modules.movies.service import MovieService
from ...modules.rag.schemas import RagSearchRequest, RagSearchResponse
from ...modules.rag.service import RagService
from ...modules.recommendations.schemas import RecommendationRequest, RecommendationResponse
from ...modules.recommendations.service import RecommendationService


class AgentTools:
    def __init__(
        self,
        rag_service: RagService | None = None,
        recommendation_service: RecommendationService | None = None,
        movie_service: MovieService | None = None,
    ) -> None:
        self.rag_service = rag_service or RagService()
        self.recommendation_service = recommendation_service or RecommendationService()
        self.movie_service = movie_service or MovieService()

    async def rag_search(self, query: str, top_k: int) -> RagSearchResponse:
        return self.rag_service.search(RagSearchRequest(query=query, topK=top_k))

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        return self.recommendation_service.recommend(request)

    async def movie_search(
        self,
        *,
        search: str | None = None,
        genre: str | None = None,
        language: str | None = None,
        min_rating: float | None = None,
        sort: str | None = None,
    ) -> MovieListResponse:
        return self.movie_service.list_movies(
            search=search,
            genre=genre,
            language=language,
            min_rating=min_rating,
            sort=sort,
        )

    async def call(self, tool_name: str, payload: dict):
        if tool_name == "rag_search":
            return await self.rag_search(payload.get("query", ""), int(payload.get("top_k", 5)))
        if tool_name == "recommend":
            return await self.recommend(RecommendationRequest(**payload))
        if tool_name == "movie_search":
            return await self.movie_search(**payload)
        raise ValueError(f"Unsupported agent tool: {tool_name}")
