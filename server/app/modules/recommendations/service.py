from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from fastapi import HTTPException

from server.app.core.config import get_config
from server.app.modules.agent.llm_client import DeepSeekClient, DeepSeekError, DeepSeekUnavailableError
from server.app.modules.agent.planner import AgentPlan, AgentPlanner
from server.app.modules.agent.prompts import build_recommendation_messages
from server.app.modules.movies.schemas import Movie
from server.app.modules.movies.service import MovieService
from server.app.modules.rag.schemas import RagSearchRequest, RagSearchResult
from server.app.modules.rag.service import RagService
from server.app.modules.recommendations.mappers import recommender_item_to_schema
from server.app.modules.recommendations.recommender_client import RecommenderClient
from server.app.modules.recommendations.schemas import RecommendationItem, RecommendationRequest, RecommendationResponse
from server.app.shared.text_utils import normalize_text


MAX_REASON_CHARS = 300


class RecommendationService:
    def __init__(
        self,
        recommender_client: RecommenderClient | None = None,
        movie_service: MovieService | None = None,
        planner: AgentPlanner | None = None,
        rag_service: RagService | None = None,
        llm_client: DeepSeekClient | None = None,
    ) -> None:
        self.config = get_config()
        self.recommender_client = recommender_client or RecommenderClient()
        self.movie_service = movie_service or MovieService()
        self.planner = planner or AgentPlanner()
        self.rag_service = rag_service or RagService()
        self.llm_client = llm_client or DeepSeekClient(self.config)

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        if request.mode == "content":
            return RecommendationResponse(items=self._recommend_content(request.seedMovieName, request.topK))

        if request.mode == "collaborative":
            user_id = self._parse_user_id(request.userId)
            return RecommendationResponse(items=self._recommend_collaborative(user_id, request.seedMovieName, request.topK))

        return self._recommend_agent_ready(request)

    def _recommend_content(self, seed_movie_name: str, top_k: int) -> list[RecommendationItem]:
        return [
            recommender_item_to_schema(item)
            for item in self.recommender_client.recommend_content(seed_movie_name, top_k)
        ]

    def _recommend_collaborative(
        self,
        user_id: int,
        seed_movie_name: str,
        top_k: int,
    ) -> list[RecommendationItem]:
        return [
            recommender_item_to_schema(item)
            for item in self.recommender_client.recommend_collaborative(
                user_id=user_id,
                movie_name=seed_movie_name or None,
                top_k=top_k,
            )
        ]

    def _recommend_agent_ready(self, request: RecommendationRequest) -> RecommendationResponse:
        plan = self.planner.plan(
            request.prompt,
            seed_movie_name=request.seedMovieName,
            user_id=request.userId,
            top_k=request.topK,
            default_intent="recommendation",
        )
        plan = self._normalize_plan_for_recommendation(plan)

        items: list[RecommendationItem] = []
        if plan.strategy == "content":
            try:
                items = self._recommend_content(plan.seed_movie_name, request.topK)
            except HTTPException as exc:
                if exc.status_code not in {404, 503}:
                    raise
        elif plan.strategy == "collaborative" and plan.user_id is not None:
            try:
                items = self._recommend_collaborative(plan.user_id, plan.seed_movie_name, request.topK)
            except HTTPException as exc:
                if exc.status_code not in {404, 503}:
                    raise

        items = self._apply_agent_filters(items, plan)
        if len(items) < request.topK:
            items.extend(
                self._build_local_recommendations(
                    plan,
                    top_k=request.topK - len(items),
                    excluded_ids={str(item.movie.id) for item in items},
                )
            )

        deduped_items = self._dedupe_items(items)[: request.topK]
        rag_results = self._filter_rag_results(
            self._safe_rag_search(self._build_rag_query(request.prompt, plan), top_k=3),
            plan,
        )
        rag_summary = self._build_rag_summary(rag_results)
        item_rag_summaries = self._build_item_rag_summaries(deduped_items, plan)
        llm_summary = self._build_llm_summary(request.prompt, plan, deduped_items, rag_results)

        final_items = [
            item.model_copy(
                update={
                    "reason": self._compose_reason(
                        item,
                        plan,
                        item_rag_summaries.get(str(item.movie.id), rag_summary),
                        llm_summary,
                    ),
                    "source": "agent-ready",
                }
            )
            for item in deduped_items
        ]
        return RecommendationResponse(items=final_items)

    @staticmethod
    def _normalize_plan_for_recommendation(plan: AgentPlan) -> AgentPlan:
        if plan.intent == "project_qa":
            return replace(
                plan,
                intent="recommendation",
                strategy="local",
                explanation="检测到输入更像项目问答，因此回退到本地电影库推荐。",
            )
        return plan

    def _build_local_recommendations(
        self,
        plan: AgentPlan,
        top_k: int,
        excluded_ids: set[str],
    ) -> list[RecommendationItem]:
        if top_k <= 0:
            return []

        primary_genre = plan.genres[0] if plan.genres else None
        sort = "rating" if (plan.genres or plan.min_rating is not None) else "popularity"
        response = self.movie_service.list_movies(
            search=None,
            genre=primary_genre,
            language=plan.language,
            min_rating=plan.min_rating,
            sort=sort,
        )
        movies = [
            movie
            for movie in response.items
            if str(movie.id) not in excluded_ids and self._movie_matches_plan(movie, plan)
        ]
        movies = sorted(movies, key=lambda movie: self._movie_rank(movie, plan), reverse=True)
        return [
            RecommendationItem(
                movie=movie,
                score=self._local_score(movie, plan),
                reason=self._local_reason(movie, plan),
                source="agent-ready",
            )
            for movie in movies[:top_k]
        ]

    def _apply_agent_filters(
        self,
        items: list[RecommendationItem],
        plan: AgentPlan,
    ) -> list[RecommendationItem]:
        return self._dedupe_items([item for item in items if self._movie_matches_plan(item.movie, plan)])

    def _movie_matches_plan(self, movie: Movie, plan: AgentPlan) -> bool:
        movie_genres = {genre.lower() for genre in movie.genres}
        wanted = {genre.lower() for genre in plan.genres}
        excluded = {genre.lower() for genre in plan.excluded_genres}
        if wanted and not movie_genres.intersection(wanted):
            return False
        if excluded and movie_genres.intersection(excluded):
            return False
        if plan.language and normalize_text(movie.language).lower() != plan.language:
            return False
        if plan.min_rating is not None and (movie.ratingMean is None or movie.ratingMean < plan.min_rating):
            return False
        return True

    @staticmethod
    def _movie_rank(movie: Movie, plan: AgentPlan) -> tuple[float, float, float]:
        wanted = {genre.lower() for genre in plan.genres}
        current = {genre.lower() for genre in movie.genres}
        return (
            float(len(wanted.intersection(current))),
            float(movie.ratingMean or 0.0),
            float(movie.tmdbPopularity or 0.0),
        )

    @staticmethod
    def _local_score(movie: Movie, plan: AgentPlan) -> float:
        rating_component = (movie.ratingMean or 0.0) / 5
        popularity_component = min((movie.tmdbPopularity or 0.0) / 100, 1.0)
        genre_bonus = 0.05 if plan.genres and any(genre in movie.genres for genre in plan.genres) else 0.0
        return round(min(rating_component * 0.7 + popularity_component * 0.3 + genre_bonus, 1.0), 6)

    @staticmethod
    def _local_reason(movie: Movie, plan: AgentPlan) -> str:
        parts: list[str] = []
        if movie.ratingMean is not None:
            parts.append(f"本地平均评分：{movie.ratingMean:.1f}")
        if plan.language and normalize_text(movie.language).lower() == plan.language:
            parts.append(f"语言匹配：{plan.language}")
        return "；".join(parts)

    def _compose_reason(
        self,
        item: RecommendationItem,
        plan: AgentPlan,
        rag_summary: str,
        llm_summary: str,
    ) -> str:
        details: list[str] = [plan.explanation]
        matched = [genre for genre in item.movie.genres if genre.lower() in {value.lower() for value in plan.genres}]
        if matched:
            details.append(f"匹配类型：{', '.join(matched[:3])}")
        if plan.min_rating is not None and item.movie.ratingMean is not None and not item.reason:
            details.append(f"评分 {item.movie.ratingMean:.1f} 满足你的要求")
        if item.reason:
            details.append(item.reason)
        if llm_summary:
            details.append(llm_summary)
        elif rag_summary:
            details.append(rag_summary)
        return self._trim_reason(" ".join(self._dedupe_reason_parts(details)))

    def _build_rag_query(self, prompt: str, plan: AgentPlan) -> str:
        parts: list[str] = []
        if plan.seed_movie_name:
            parts.append(plan.seed_movie_name)
        parts.extend(plan.genres)
        if plan.language:
            parts.append(plan.language)
        if plan.min_rating is not None:
            parts.append("高分")
        parts.append("电影推荐")
        if not parts:
            parts.append(normalize_text(prompt))
        return " ".join(part for part in parts if part).strip()

    def _safe_rag_search(self, query: str, top_k: int) -> list[RagSearchResult]:
        if not query:
            return []
        try:
            response = self.rag_service.search(RagSearchRequest(query=query, topK=top_k))
        except Exception:
            return []
        return response.items

    def _filter_rag_results(self, rag_results: list[RagSearchResult], plan: AgentPlan) -> list[RagSearchResult]:
        if not rag_results:
            return []

        filtered = [result for result in rag_results if not self._rag_result_has_excluded_genre(result, plan)]
        if plan.genres:
            filtered.sort(key=lambda result: self._rag_result_rank(result, plan), reverse=True)
        return filtered

    def _build_rag_summary(self, rag_results: list[RagSearchResult]) -> str:
        if not rag_results:
            return ""
        result = rag_results[0]
        title = result.title or result.source.name
        snippet = result.content.replace("\n", " ").strip()
        snippet = snippet[:100].rstrip("，。；,; ")
        if not snippet:
            return ""
        return self._trim_reason(f"RAG 补充：{title} 提到 {snippet}", max_chars=120)

    def _build_item_rag_summaries(
        self,
        items: list[RecommendationItem],
        plan: AgentPlan,
    ) -> dict[str, str]:
        summaries: dict[str, str] = {}
        for item in items:
            summary = self._build_item_rag_summary(item.movie, plan)
            if summary:
                summaries[str(item.movie.id)] = summary
        return summaries

    def _build_item_rag_summary(self, movie: Movie, plan: AgentPlan) -> str:
        query_parts = [movie.title]
        query_parts.extend(movie.genres[:2])
        if movie.language:
            query_parts.append(movie.language)
        query = " ".join(part for part in query_parts if normalize_text(part)).strip()
        if not query:
            return ""

        rag_results = self._filter_rag_results(self._safe_rag_search(query, top_k=2), plan)
        related_results = [result for result in rag_results if self._rag_result_relates_to_movie(result, movie)]
        if not related_results:
            related_results = rag_results[:1]
        return self._build_rag_summary(related_results)

    def _build_llm_summary(
        self,
        prompt: str,
        plan: AgentPlan,
        items: list[RecommendationItem],
        rag_results: list[RagSearchResult],
    ) -> str:
        if not items or not self.llm_client.is_enabled():
            return ""
        rag_context = self._rag_context_text(rag_results)
        try:
            return self._trim_reason(
                self.llm_client.chat_sync(
                    build_recommendation_messages(
                        user_prompt=prompt or "请推荐一些电影。",
                        plan=plan,
                        rag_context=rag_context,
                        items=items,
                    ),
                    temperature=0.2,
                )
            )
        except (DeepSeekUnavailableError, DeepSeekError):
            return ""

    def _rag_context_text(self, rag_results: list[RagSearchResult]) -> str:
        parts: list[str] = []
        remaining = self.config.agent_max_context_chars
        for result in rag_results[: self.config.agent_max_rag_results]:
            chunk = f"[{result.title or result.source.name}] {result.content}"
            if len(chunk) > remaining:
                chunk = chunk[:remaining]
            parts.append(chunk)
            remaining -= len(chunk)
            if remaining <= 0:
                break
        return "\n".join(parts)

    @staticmethod
    def _dedupe_reason_parts(parts: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for part in parts:
            cleaned = normalize_text(part)
            if not cleaned:
                continue
            key = "".join(char.lower() for char in cleaned if char.isalnum())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(cleaned)
        return deduped

    @staticmethod
    def _rag_result_has_excluded_genre(result: RagSearchResult, plan: AgentPlan) -> bool:
        excluded = {genre.lower() for genre in plan.excluded_genres}
        if not excluded:
            return False

        metadata_genres = {
            normalize_text(value).lower()
            for value in result.metadata.get("genres", [])
            if normalize_text(value)
        }
        if metadata_genres.intersection(excluded):
            return True

        genre_value = normalize_text(result.metadata.get("genre")).lower()
        if genre_value and genre_value in excluded:
            return True
        return False

    @staticmethod
    def _rag_result_rank(result: RagSearchResult, plan: AgentPlan) -> tuple[float, float]:
        wanted = {genre.lower() for genre in plan.genres}
        metadata_genres = {
            normalize_text(value).lower()
            for value in result.metadata.get("genres", [])
            if normalize_text(value)
        }
        genre_value = normalize_text(result.metadata.get("genre")).lower()
        match_count = float(len(wanted.intersection(metadata_genres)))
        if genre_value and genre_value in wanted:
            match_count += 1.0
        return match_count, float(result.score)

    @staticmethod
    def _rag_result_relates_to_movie(result: RagSearchResult, movie: Movie) -> bool:
        movie_title = normalize_text(movie.title).lower()
        result_title = normalize_text(result.title).lower()
        metadata_title = normalize_text(result.metadata.get("title")).lower()
        if movie_title and (movie_title in result_title or movie_title in metadata_title):
            return True

        movie_genres = {normalize_text(genre).lower() for genre in movie.genres if normalize_text(genre)}
        result_genres = {
            normalize_text(value).lower()
            for value in result.metadata.get("genres", [])
            if normalize_text(value)
        }
        return bool(movie_genres and result_genres and movie_genres.intersection(result_genres))

    @staticmethod
    def _trim_reason(reason: str, max_chars: int = MAX_REASON_CHARS) -> str:
        text = normalize_text(reason)
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3].rstrip() + "..."

    @staticmethod
    def _parse_user_id(user_id: str) -> int:
        try:
            parsed = int(normalize_text(user_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="userId must be a positive integer.") from exc
        if parsed < 1:
            raise HTTPException(status_code=400, detail="userId must be a positive integer.")
        return parsed

    @staticmethod
    def _dedupe_items(items: Iterable[RecommendationItem]) -> list[RecommendationItem]:
        deduped: list[RecommendationItem] = []
        seen: set[str] = set()
        for item in items:
            identifier = str(item.movie.id)
            if identifier in seen:
                continue
            seen.add(identifier)
            deduped.append(item)
        return deduped


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
