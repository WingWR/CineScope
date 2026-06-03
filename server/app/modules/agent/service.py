from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentRecommendationRequest,
    AgentRecommendationResponse,
)


class AgentService:
    def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        not_implemented("agent.service", "chat")

    def recommend(self, request: AgentRecommendationRequest) -> AgentRecommendationResponse:
        not_implemented("agent.service", "recommend")


def get_agent_service() -> AgentService:
    return AgentService()
