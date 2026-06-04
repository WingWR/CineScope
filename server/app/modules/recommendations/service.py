from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from fastapi import HTTPException

from server.app.modules.movies.schemas import Movie
from server.app.modules.movies.service import MovieService
from server.app.modules.recommendations.mappers import recommender_item_to_schema
from server.app.modules.recommendations.recommender_client import RecommenderClient
from server.app.modules.recommendations.schemas import RecommendationItem, RecommendationRequest, RecommendationResponse
from server.app.shared.text_utils import normalize_text


Strategy = Literal["content", "collaborative", "local"]

GENRE_ALIASES = {
    "Action": ["action", "动作"],
    "Adventure": ["adventure", "冒险"],
    "Animation": ["animation", "animated", "动画"],
    "Children": ["children", "kids", "儿童"],
    "Comedy": ["comedy", "喜剧", "搞笑"],
    "Crime": ["crime", "犯罪"],
    "Documentary": ["documentary", "纪录片"],
    "Drama": ["drama", "剧情", "文艺"],
    "Fantasy": ["fantasy", "奇幻", "魔幻"],
    "Film-Noir": ["film-noir", "noir", "黑色电影"],
    "Horror": ["horror", "恐怖", "惊悚恐怖"],
    "IMAX": ["imax"],
    "Musical": ["musical", "音乐剧", "歌舞"],
    "Mystery": ["mystery", "悬疑"],
    "Romance": ["romance", "爱情", "浪漫"],
    "Sci-Fi": ["sci-fi", "science fiction", "科幻", "科幻片"],
    "Thriller": ["thriller", "惊悚"],
    "War": ["war", "战争"],
    "Western": ["western", "西部"],
}
NEGATION_PREFIXES = ["not ", "without ", "no ", "不要", "别", "不想看", "排除"]
LANGUAGE_ALIASES = {
    "en": ["english", "英文", "英语"],
    "zh": ["chinese", "mandarin", "中文", "汉语", "国语"],
    "ja": ["japanese", "日语", "日本"],
    "ko": ["korean", "韩语", "韩国"],
    "fr": ["french", "法语", "法国"],
}
PERSONALIZATION_KEYWORDS = [
    "personal",
    "personalized",
    "user",
    "profile",
    "history",
    "个性化",
    "用户",
    "按我",
    "给我推荐",
]


@dataclass(frozen=True)
class AgentPlan:
    strategy: Strategy
    explanation: str
    seed_movie_name: str = ""
    user_id: int | None = None
    genres: list[str] = field(default_factory=list)
    excluded_genres: list[str] = field(default_factory=list)
    language: str | None = None
    min_rating: float | None = None


class RecommendationService:
    def __init__(
        self,
        recommender_client: RecommenderClient | None = None,
        movie_service: MovieService | None = None,
    ) -> None:
        self.recommender_client = recommender_client or RecommenderClient()
        self.movie_service = movie_service or MovieService()

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        if request.mode == "content":
            items = self._recommend_content(request.seedMovieName, request.topK)
            return RecommendationResponse(items=items)

        if request.mode == "collaborative":
            user_id = self._parse_user_id(request.userId)
            items = self._recommend_collaborative(user_id, request.seedMovieName, request.topK)
            return RecommendationResponse(items=items)

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
        plan = self._plan_agent_request(request)
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
            supplement = self._build_local_recommendations(
                plan,
                top_k=request.topK - len(items),
                excluded_ids={str(item.movie.id) for item in items},
            )
            items.extend(supplement)

        agent_items = [
            item.model_copy(
                update={
                    "reason": self._build_agent_reason(item, plan),
                    "source": "agent-ready",
                }
            )
            for item in self._dedupe_items(items)[: request.topK]
        ]
        return RecommendationResponse(items=agent_items)

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
        filtered = [item for item in items if self._movie_matches_plan(item.movie, plan)]
        return self._dedupe_items(filtered)

    def _plan_agent_request(self, request: RecommendationRequest) -> AgentPlan:
        prompt = normalize_text(request.prompt)
        lower_prompt = prompt.lower()
        genres = [genre for genre in self._extract_genres(lower_prompt) if genre not in self._extract_excluded_genres(lower_prompt)]
        excluded_genres = self._extract_excluded_genres(lower_prompt)
        language = self._extract_language(lower_prompt)
        min_rating = self._extract_min_rating(lower_prompt)
        seed_movie_name = normalize_text(request.seedMovieName) or self._extract_seed_movie_name(prompt)
        user_id = self._try_parse_user_id(request.userId)
        wants_personalized = any(keyword in lower_prompt for keyword in PERSONALIZATION_KEYWORDS)

        if seed_movie_name and wants_personalized and user_id is not None:
            return AgentPlan(
                strategy="collaborative",
                explanation="Matched your seed movie with collaborative preference signals.",
                seed_movie_name=seed_movie_name,
                user_id=user_id,
                genres=genres,
                excluded_genres=excluded_genres,
                language=language,
                min_rating=min_rating,
            )
        if seed_movie_name:
            return AgentPlan(
                strategy="content",
                explanation="Expanded from a seed movie using similarity signals.",
                seed_movie_name=seed_movie_name,
                user_id=user_id,
                genres=genres,
                excluded_genres=excluded_genres,
                language=language,
                min_rating=min_rating,
            )
        if wants_personalized and user_id is not None:
            return AgentPlan(
                strategy="collaborative",
                explanation="Built a personalized list from collaborative signals.",
                user_id=user_id,
                genres=genres,
                excluded_genres=excluded_genres,
                language=language,
                min_rating=min_rating,
            )
        return AgentPlan(
            strategy="local",
            explanation="Ranked the catalog by the genres, language, and quality cues in your prompt.",
            user_id=user_id,
            genres=genres,
            excluded_genres=excluded_genres,
            language=language,
            min_rating=min_rating,
        )

    @staticmethod
    def _extract_seed_movie_name(prompt: str) -> str:
        for pattern in (
            r"《([^》]+)》",
            r'"([^"]+)"',
            r"'([^']+)'",
        ):
            match = re.search(pattern, prompt)
            if match:
                return normalize_text(match.group(1))
        return ""

    @staticmethod
    def _extract_genres(prompt: str) -> list[str]:
        matches: list[str] = []
        for genre, aliases in GENRE_ALIASES.items():
            if any(alias in prompt for alias in aliases):
                matches.append(genre)
        return matches

    @staticmethod
    def _extract_excluded_genres(prompt: str) -> list[str]:
        excluded: list[str] = []
        for genre, aliases in GENRE_ALIASES.items():
            for alias in aliases:
                if any(f"{prefix}{alias}" in prompt for prefix in NEGATION_PREFIXES):
                    excluded.append(genre)
                    break
        return excluded

    @staticmethod
    def _extract_language(prompt: str) -> str | None:
        for code, aliases in LANGUAGE_ALIASES.items():
            if any(alias in prompt for alias in aliases):
                return code
        return None

    @staticmethod
    def _extract_min_rating(prompt: str) -> float | None:
        match = re.search(r"([0-5](?:\.\d)?)\s*(?:分|rating|rated)", prompt)
        if match:
            return float(match.group(1))
        if "high rating" in prompt or "高分" in prompt or "评分高" in prompt:
            return 4.0
        return None

    @staticmethod
    def _parse_user_id(user_id: str) -> int:
        try:
            parsed = int(normalize_text(user_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="userId must be a positive integer.") from exc
        if parsed < 1:
            raise HTTPException(status_code=400, detail="userId must be a positive integer.")
        return parsed

    @classmethod
    def _try_parse_user_id(cls, user_id: str) -> int | None:
        try:
            return cls._parse_user_id(user_id)
        except HTTPException:
            return None

    def _movie_matches_plan(self, movie: Movie, plan: AgentPlan) -> bool:
        movie_genres = {genre.lower() for genre in movie.genres}
        if plan.genres:
            wanted = {genre.lower() for genre in plan.genres}
            if not movie_genres.intersection(wanted):
                return False
        if plan.excluded_genres:
            excluded = {genre.lower() for genre in plan.excluded_genres}
            if movie_genres.intersection(excluded):
                return False
        if plan.language and normalize_text(movie.language).lower() != plan.language:
            return False
        if plan.min_rating is not None and (movie.ratingMean is None or movie.ratingMean < plan.min_rating):
            return False
        return True

    def _movie_rank(self, movie: Movie, plan: AgentPlan) -> tuple[float, float, float]:
        return (
            float(self._genre_overlap(movie, plan.genres)),
            float(movie.ratingMean or 0.0),
            float(movie.tmdbPopularity or 0.0),
        )

    @staticmethod
    def _genre_overlap(movie: Movie, genres: list[str]) -> int:
        wanted = {genre.lower() for genre in genres}
        current = {genre.lower() for genre in movie.genres}
        return len(wanted.intersection(current))

    def _build_agent_reason(self, item: RecommendationItem, plan: AgentPlan) -> str:
        details: list[str] = []
        if plan.explanation:
            details.append(plan.explanation)
        if plan.genres:
            matched = [genre for genre in item.movie.genres if genre.lower() in {value.lower() for value in plan.genres}]
            if matched:
                details.append(f"Matched genres: {', '.join(matched[:3])}.")
        if plan.language and normalize_text(item.movie.language).lower() == plan.language:
            details.append(f"Language matched: {plan.language}.")
        if plan.min_rating is not None and item.movie.ratingMean is not None:
            details.append(f"Rating {item.movie.ratingMean:.1f} meets your threshold.")
        if item.reason and item.reason not in details:
            details.append(item.reason)
        return " ".join(details[:4]).strip()

    def _local_reason(self, movie: Movie, plan: AgentPlan) -> str:
        parts = [plan.explanation]
        if movie.ratingMean is not None:
            parts.append(f"Catalog rating: {movie.ratingMean:.1f}.")
        if plan.genres:
            matched = [genre for genre in movie.genres if genre.lower() in {value.lower() for value in plan.genres}]
            if matched:
                parts.append(f"Genres: {', '.join(matched[:3])}.")
        return " ".join(part for part in parts if part).strip()

    @staticmethod
    def _local_score(movie: Movie, plan: AgentPlan) -> float:
        rating_component = (movie.ratingMean or 0.0) / 5
        popularity_component = min((movie.tmdbPopularity or 0.0) / 100, 1.0)
        genre_bonus = 0.05 if plan.genres and any(genre in movie.genres for genre in plan.genres) else 0.0
        return round(min(rating_component * 0.7 + popularity_component * 0.3 + genre_bonus, 1.0), 6)

    @staticmethod
    def _dedupe_items(items: list[RecommendationItem]) -> list[RecommendationItem]:
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
