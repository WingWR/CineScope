from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...modules.rag.schemas import RagSearchResult
from ...modules.recommendations.schemas import RecommendationItem


AgentIntent = Literal["recommendation", "project_qa"]


class AgentTraceStep(BaseModel):
    tool: str
    input: str | None = None
    output: str | None = None


class AgentChatRequest(BaseModel):
    message: str
    userId: str = "1"


class AgentChatResponse(BaseModel):
    answer: str
    intent: AgentIntent
    usedLlm: bool = False
    ragResults: list[RagSearchResult] = Field(default_factory=list)
    trace: list[AgentTraceStep] = Field(default_factory=list)


class AgentRecommendationRequest(BaseModel):
    message: str = ""
    prompt: str = ""
    seedMovieName: str = ""
    userId: str = "1"
    topK: int = Field(default=6, ge=1, le=50)


class AgentRecommendationResponse(BaseModel):
    answer: str
    intent: AgentIntent = "recommendation"
    usedLlm: bool = False
    items: list[RecommendationItem] = Field(default_factory=list)
    ragResults: list[RagSearchResult] = Field(default_factory=list)
    trace: list[AgentTraceStep] = Field(default_factory=list)
