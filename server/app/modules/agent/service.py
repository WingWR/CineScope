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
        trace.append(
            AgentTraceStep(
                tool="rag_search",
                input=rag_query,
                output=f"{len(rag_response.items)} results",
            )
        )

        answer, used_llm = await self._answer_project_question(request.message, rag_response.items)
        return AgentChatResponse(
            answer=answer,
            intent="project_qa",
            usedLlm=used_llm,
            ragResults=rag_response.items,
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
        trace.append(
            AgentTraceStep(
                tool="rag_search",
                input=rag_query,
                output=f"{len(rag_response.items)} results",
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

        answer, used_llm = await self._answer_recommendation(prompt, plan, recommendation_response.items, rag_response.items)
        return AgentRecommendationResponse(
            answer=answer,
            intent="recommendation",
            usedLlm=used_llm,
            items=recommendation_response.items,
            ragResults=rag_response.items,
            trace=trace,
        )

    async def _answer_project_question(
        self,
        message: str,
        rag_results: list[RagSearchResult],
    ) -> tuple[str, bool]:
        if not rag_results:
            return "当前本地资料里没有检索到足够信息。", False

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
            return "当前没有找到满足条件的本地推荐结果。", False

        rag_context = self._rag_context_text(rag_results)
        if self.llm_client.is_enabled():
            try:
                answer = await self.llm_client.chat(
                    build_recommendation_messages(
                        user_prompt=prompt or "请给出电影推荐。",
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
        parts = ["根据本地资料检索结果："]
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
            parts.append(f"还参考了本地资料：{rag_results[0].title or rag_results[0].source.name}。")
        return " ".join(parts)

    @staticmethod
    def _build_rag_query(prompt: str, plan: AgentPlan) -> str:
        parts = [prompt]
        if plan.seed_movie_name:
            parts.append(plan.seed_movie_name)
        parts.extend(plan.genres)
        parts.extend(plan.excluded_genres)
        if plan.intent == "project_qa":
            parts.extend(
                [
                    "dataset summary",
                    "quality report",
                    "genre stats",
                    "movies csv",
                    "project docs",
                ]
            )
        return " ".join(part for part in parts if part).strip()

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
