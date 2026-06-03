from __future__ import annotations

from pydantic import BaseModel, Field

from server.app.modules.recommendations.schemas import RecommendationItem


class AgentTraceStep(BaseModel):
    tool: str
    input: str | None = None
    output: str | None = None


class AgentChatRequest(BaseModel):
    message: str
    userId: str = "1"


class AgentChatResponse(BaseModel):
    answer: str
    trace: list[AgentTraceStep] = Field(default_factory=list)


class AgentRecommendationRequest(BaseModel):
    prompt: str
    seedMovieName: str = ""
    userId: str = "1"
    topK: int = Field(default=6, ge=1, le=50)


class AgentRecommendationResponse(BaseModel):
    answer: str
    items: list[RecommendationItem] = Field(default_factory=list)
    trace: list[AgentTraceStep] = Field(default_factory=list)
