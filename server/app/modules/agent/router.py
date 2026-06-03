from __future__ import annotations

from fastapi import APIRouter, Depends

from server.app.modules.agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentRecommendationRequest,
    AgentRecommendationResponse,
)
from server.app.modules.agent.service import AgentService, get_agent_service


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def chat(
    request: AgentChatRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentChatResponse:
    return service.chat(request)


@router.post("/recommend", response_model=AgentRecommendationResponse)
def recommend(
    request: AgentRecommendationRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentRecommendationResponse:
    return service.recommend(request)
