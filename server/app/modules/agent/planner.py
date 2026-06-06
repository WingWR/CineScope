from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from server.app.modules.agent.schemas import AgentIntent
from server.app.shared.text_utils import normalize_text


RecommendationStrategy = Literal["content", "collaborative", "local", "qa"]

GENRE_ALIASES = {
    "Action": ["action", "动作"],
    "Adventure": ["adventure", "冒险"],
    "Animation": ["animation", "animated", "动画"],
    "Children": ["children", "kids", "family", "儿童"],
    "Comedy": ["comedy", "funny", "喜剧", "搞笑"],
    "Crime": ["crime", "犯罪"],
    "Documentary": ["documentary", "纪录片"],
    "Drama": ["drama", "剧情", "文艺"],
    "Fantasy": ["fantasy", "奇幻", "魔幻"],
    "Film-Noir": ["film-noir", "noir", "黑色电影"],
    "Horror": ["horror", "scary", "恐怖", "惊悚恐怖"],
    "IMAX": ["imax"],
    "Musical": ["musical", "音乐剧", "歌舞"],
    "Mystery": ["mystery", "悬疑"],
    "Romance": ["romance", "romantic", "爱情", "浪漫"],
    "Sci-Fi": ["sci-fi", "science fiction", "scifi", "科幻"],
    "Thriller": ["thriller", "惊悚"],
    "War": ["war", "战争"],
    "Western": ["western", "西部"],
}

NEGATION_PREFIXES = [
    "not ",
    "without ",
    "no ",
    "avoid ",
    "exclude ",
    "不要",
    "别",
    "不想看",
    "排除",
]

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
    "for me",
    "my profile",
    "my history",
    "用户",
    "个性化",
    "按我",
    "给我推荐",
]

PROJECT_QA_KEYWORDS = [
    "dataset",
    "field",
    "fields",
    "schema",
    "clean",
    "cleaning",
    "quality",
    "summary",
    "statistics",
    "algorithm",
    "evaluation",
    "movielens",
    "imdb",
    "tmdb",
    "数据",
    "数据集",
    "字段",
    "列",
    "清洗",
    "质量",
    "摘要",
    "统计",
    "算法",
    "评估",
    "项目",
]

RECOMMENDATION_KEYWORDS = [
    "recommend",
    "movie",
    "similar",
    "like",
    "watch",
    "推荐",
    "想看",
    "喜欢",
    "类似",
    "高分",
    "电影",
    "科幻",
    "喜剧",
    "剧情",
    "动作",
    "恐怖",
    "爱情",
]


@dataclass(frozen=True)
class AgentPlan:
    intent: AgentIntent
    strategy: RecommendationStrategy
    message: str
    explanation: str
    seed_movie_name: str = ""
    user_id: int | None = None
    genres: list[str] = field(default_factory=list)
    excluded_genres: list[str] = field(default_factory=list)
    language: str | None = None
    min_rating: float | None = None
    top_k: int = 6
    personalized: bool = False

    def recommendation_summary(self) -> str:
        parts: list[str] = []
        if self.seed_movie_name:
            parts.append(f"seed={self.seed_movie_name}")
        if self.genres:
            parts.append(f"genres={', '.join(self.genres)}")
        if self.excluded_genres:
            parts.append(f"exclude={', '.join(self.excluded_genres)}")
        if self.language:
            parts.append(f"language={self.language}")
        if self.min_rating is not None:
            parts.append(f"min_rating={self.min_rating:.1f}")
        if self.personalized and self.user_id is not None:
            parts.append(f"user_id={self.user_id}")
        return "; ".join(parts) or "no explicit filters"


class AgentPlanner:
    def plan(
        self,
        message: str,
        *,
        seed_movie_name: str = "",
        user_id: str = "1",
        top_k: int = 6,
        default_intent: AgentIntent = "recommendation",
    ) -> AgentPlan:
        normalized_message = normalize_text(message)
        lowered = normalized_message.lower()

        extracted_seed = normalize_text(seed_movie_name) or self._extract_seed_movie_name(normalized_message)
        excluded_genres = self._extract_excluded_genres(lowered)
        genres = [genre for genre in self._extract_genres(lowered) if genre not in excluded_genres]
        language = self._extract_language(lowered)
        min_rating = self._extract_min_rating(normalized_message, lowered)
        parsed_user_id = self._parse_user_id(user_id)
        personalized = parsed_user_id is not None and any(keyword in lowered for keyword in PERSONALIZATION_KEYWORDS)

        qa_score = self._keyword_score(lowered, PROJECT_QA_KEYWORDS)
        recommendation_score = self._keyword_score(lowered, RECOMMENDATION_KEYWORDS)
        if genres or excluded_genres or extracted_seed or personalized:
            recommendation_score += 2
        if any(keyword in lowered for keyword in {"recommend", "类似", "推荐", "想看"}):
            recommendation_score += 2

        if recommendation_score > qa_score:
            intent: AgentIntent = "recommendation"
        elif qa_score > recommendation_score:
            intent = "project_qa"
        else:
            intent = default_intent

        if intent == "project_qa":
            return AgentPlan(
                intent="project_qa",
                strategy="qa",
                message=normalized_message,
                explanation="根据本地项目文档和数据集摘要回答问题。",
                seed_movie_name=extracted_seed,
                user_id=parsed_user_id,
                genres=genres,
                excluded_genres=excluded_genres,
                language=language,
                min_rating=min_rating,
                top_k=top_k,
                personalized=personalized,
            )

        if extracted_seed and personalized and parsed_user_id is not None:
            strategy: RecommendationStrategy = "collaborative"
            explanation = "结合种子电影和用户偏好生成推荐。"
        elif extracted_seed:
            strategy = "content"
            explanation = "基于种子电影扩展相似推荐。"
        elif personalized and parsed_user_id is not None:
            strategy = "collaborative"
            explanation = "基于用户画像和协同过滤信号生成推荐。"
        else:
            strategy = "local"
            explanation = "根据本地电影库的类型、语言和评分条件筛选推荐。"

        return AgentPlan(
            intent="recommendation",
            strategy=strategy,
            message=normalized_message,
            explanation=explanation,
            seed_movie_name=extracted_seed,
            user_id=parsed_user_id,
            genres=genres,
            excluded_genres=excluded_genres,
            language=language,
            min_rating=min_rating,
            top_k=top_k,
            personalized=personalized,
        )

    @staticmethod
    def _keyword_score(message: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if keyword in message)

    @staticmethod
    def _extract_seed_movie_name(message: str) -> str:
        for pattern in (r"《([^》]+)》", r'"([^"]+)"', r"'([^']+)'"):
            match = re.search(pattern, message)
            if match:
                return normalize_text(match.group(1))
        return ""

    @staticmethod
    def _extract_genres(message: str) -> list[str]:
        matches: list[str] = []
        for genre, aliases in GENRE_ALIASES.items():
            if any(alias in message for alias in aliases):
                matches.append(genre)
        return matches

    @staticmethod
    def _extract_excluded_genres(message: str) -> list[str]:
        excluded: list[str] = []
        for genre, aliases in GENRE_ALIASES.items():
            for alias in aliases:
                if any(f"{prefix}{alias}" in message for prefix in NEGATION_PREFIXES):
                    excluded.append(genre)
                    break
        return excluded

    @staticmethod
    def _extract_language(message: str) -> str | None:
        for code, aliases in LANGUAGE_ALIASES.items():
            if any(alias in message for alias in aliases):
                return code
        return None

    @staticmethod
    def _extract_min_rating(message: str, lowered: str) -> float | None:
        match = re.search(r"([0-5](?:\.\d)?)\s*(?:分|星|rating|rated)", message)
        if match:
            return float(match.group(1))
        if any(keyword in lowered for keyword in {"高分", "评分高", "high rating", "strong ratings", "highly rated"}):
            return 4.0
        return None

    @staticmethod
    def _parse_user_id(user_id: str) -> int | None:
        try:
            parsed = int(normalize_text(user_id))
        except ValueError:
            return None
        if parsed < 1:
            return None
        return parsed
