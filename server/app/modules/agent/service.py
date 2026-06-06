from __future__ import annotations

from server.app.core.config import get_config
from server.app.modules.agent.llm_client import DeepSeekClient, DeepSeekError, DeepSeekUnavailableError
from server.app.modules.agent.planner import AgentPlan, AgentPlanner
from server.app.modules.agent.prompts import build_project_qa_messages, build_recommendation_messages
from server.app.modules.agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentRecommendationRequest,
    AgentRecommendationResponse,
    AgentTraceStep,
)
from server.app.modules.agent.tools import AgentTools
from server.app.modules.rag.schemas import RagSearchResult
from server.app.modules.recommendations.schemas import RecommendationRequest
from server.app.shared.text_utils import normalize_text


PROJECT_QA_PRIORITY_SOURCES = {
    "dataset_summary": 3.0,
    "quality_report": 2.5,
    "genre_stats": 2.0,
}


class AgentService:
    def __init__(
        self,
        planner: AgentPlanner | None = None,
        tools: AgentTools | None = None,
        llm_client: DeepSeekClient | None = None,
    ) -> None:
        self.config = get_config()
        self.planner = planner or AgentPlanner()
        self.tools = tools or AgentTools()
        self.llm_client = llm_client or DeepSeekClient(self.config)

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        plan = self.planner.plan(
            request.message,
            user_id=request.userId,
            default_intent="project_qa",
        )
        if plan.intent == "recommendation":
            recommendation = await self.recommend(
                AgentRecommendationRequest(
                    message=request.message,
                    prompt=request.message,
                    userId=request.userId,
                    topK=6,
                )
            )
            return AgentChatResponse(
                answer=recommendation.answer,
                intent="recommendation",
                usedLlm=recommendation.usedLlm,
                ragResults=recommendation.ragResults,
                trace=recommendation.trace,
            )

        trace: list[AgentTraceStep] = []
        rag_query = self._build_rag_query(request.message, plan)
        rag_response = await self.tools.rag_search(rag_query, self.config.agent_max_rag_results)
        rag_items = self._rerank_project_qa_results(request.message, rag_response.items)
        trace.append(
            AgentTraceStep(
                tool="rag_search",
                input=rag_query,
                output=f"{len(rag_items)} results",
            )
        )

        answer, used_llm = await self._answer_project_question(request.message, rag_items)
        return AgentChatResponse(
            answer=answer,
            intent="project_qa",
            usedLlm=used_llm,
            ragResults=rag_items,
            trace=trace,
        )

    async def recommend(self, request: AgentRecommendationRequest) -> AgentRecommendationResponse:
        prompt = request.prompt or request.message
        plan = self.planner.plan(
            prompt,
            seed_movie_name=request.seedMovieName,
            user_id=request.userId,
            top_k=request.topK,
            default_intent="recommendation",
        )
        trace: list[AgentTraceStep] = []

        rag_query = self._build_rag_query(prompt, plan)
        rag_response = await self.tools.rag_search(rag_query, self.config.agent_max_rag_results)
        rag_items = self._filter_recommendation_rag_results(rag_response.items, plan)
        trace.append(
            AgentTraceStep(
                tool="rag_search",
                input=rag_query,
                output=f"{len(rag_items)} results",
            )
        )

        recommendation_request = RecommendationRequest(
            mode="agent-ready",
            prompt=prompt,
            seedMovieName=request.seedMovieName,
            userId=request.userId,
            topK=request.topK,
        )
        recommendation_response = await self.tools.recommend(recommendation_request)
        trace.append(
            AgentTraceStep(
                tool="recommend",
                input=plan.recommendation_summary(),
                output=f"{len(recommendation_response.items)} items",
            )
        )

        answer, used_llm = await self._answer_recommendation(prompt, plan, recommendation_response.items, rag_items)
        return AgentRecommendationResponse(
            answer=answer,
            intent="recommendation",
            usedLlm=used_llm,
            items=recommendation_response.items,
            ragResults=rag_items,
            trace=trace,
        )

    async def _answer_project_question(
        self,
        message: str,
        rag_results: list[RagSearchResult],
    ) -> tuple[str, bool]:
        if not rag_results:
            return "当前没有检索到足够的本地项目资料来回答这个问题。", False

        rag_context = self._rag_context_text(rag_results)
        if self.llm_client.is_enabled():
            try:
                answer = await self.llm_client.chat(
                    build_project_qa_messages(user_message=message, rag_context=rag_context),
                    temperature=0.2,
                )
                if answer:
                    return answer, True
            except (DeepSeekUnavailableError, DeepSeekError):
                pass
        return self._fallback_project_answer(rag_results), False

    async def _answer_recommendation(
        self,
        prompt: str,
        plan: AgentPlan,
        items,
        rag_results: list[RagSearchResult],
    ) -> tuple[str, bool]:
        if not items:
            return "当前没有找到满足这些条件的本地推荐结果。", False

        rag_context = self._rag_context_text(rag_results)
        if self.llm_client.is_enabled():
            try:
                answer = await self.llm_client.chat(
                    build_recommendation_messages(
                        user_prompt=prompt or "Please recommend some movies.",
                        plan=plan,
                        rag_context=rag_context,
                        items=items,
                    ),
                    temperature=0.2,
                )
                if answer:
                    return answer, True
            except (DeepSeekUnavailableError, DeepSeekError):
                pass
        return self._fallback_recommendation_answer(plan, items, rag_results), False

    def _fallback_project_answer(self, rag_results: list[RagSearchResult]) -> str:
        parts = ["根据本地项目资料检索结果："]
        for result in rag_results[:3]:
            headline = result.title or result.source.name
            snippet = result.content.replace("\n", " ").strip()[:120]
            parts.append(f"{headline} 提到：{snippet}")
        return " ".join(parts)

    def _fallback_recommendation_answer(self, plan: AgentPlan, items, rag_results: list[RagSearchResult]) -> str:
        titles = "、".join(item.movie.title for item in items[:3])
        parts = [f"我已经按你的条件生成本地推荐，优先结果包括：{titles}。"]
        if plan.genres:
            parts.append(f"重点匹配类型：{', '.join(plan.genres)}。")
        if plan.excluded_genres:
            parts.append(f"已排除类型：{', '.join(plan.excluded_genres)}。")
        if rag_results:
            parts.append(f"参考了本地资料：{rag_results[0].title or rag_results[0].source.name}。")
        return " ".join(parts)

    def _build_rag_query(self, prompt: str, plan: AgentPlan) -> str:
        if plan.intent == "project_qa":
            parts = [
                normalize_text(prompt),
                "dataset summary",
                "quality report",
                "genre stats",
                "project docs",
            ]
            return " ".join(part for part in parts if part).strip()

        parts: list[str] = []
        if plan.seed_movie_name:
            parts.append(plan.seed_movie_name)
        parts.extend(plan.genres)
        if plan.language:
            parts.append(plan.language)
        if plan.min_rating is not None:
            parts.append("high rated")
        parts.append("movie recommendation")
        if not parts:
            parts.append(normalize_text(prompt))
        return " ".join(part for part in parts if part).strip()

    def _rerank_project_qa_results(
        self,
        message: str,
        rag_results: list[RagSearchResult],
    ) -> list[RagSearchResult]:
        if not rag_results:
            return []

        stats_query = self._looks_like_stats_question(message)
        reranked = sorted(
            rag_results,
            key=lambda result: self._project_qa_rank(result, stats_query),
            reverse=True,
        )
        return reranked

    def _filter_recommendation_rag_results(
        self,
        rag_results: list[RagSearchResult],
        plan: AgentPlan,
    ) -> list[RagSearchResult]:
        if not rag_results:
            return []

        filtered = [result for result in rag_results if not self._has_excluded_genre(result, plan)]
        if plan.genres:
            filtered.sort(key=lambda result: self._recommendation_rag_rank(result, plan), reverse=True)
        return filtered

    @staticmethod
    def _looks_like_stats_question(message: str) -> bool:
        lowered = normalize_text(message).lower()
        keywords = [
            "dataset",
            "summary",
            "quality",
            "report",
            "count",
            "counts",
            "movie count",
            "rating count",
            "user count",
            "tag count",
            "how many",
            "数据集",
            "统计",
            "多少",
            "几部",
            "评分数",
            "用户数",
            "标签数",
            "概览",
            "摘要",
            "质量",
            "清洗",
        ]
        return any(keyword in lowered for keyword in keywords)

    @staticmethod
    def _project_qa_rank(result: RagSearchResult, stats_query: bool) -> tuple[float, float]:
        source_bonus = PROJECT_QA_PRIORITY_SOURCES.get(result.source.id, 0.0)
        if not stats_query and result.source.id == "dataset_summary":
            source_bonus -= 0.5
        return source_bonus, float(result.score)

    @staticmethod
    def _has_excluded_genre(result: RagSearchResult, plan: AgentPlan) -> bool:
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
    def _recommendation_rag_rank(result: RagSearchResult, plan: AgentPlan) -> tuple[float, float]:
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


def get_agent_service() -> AgentService:
    return AgentService()
