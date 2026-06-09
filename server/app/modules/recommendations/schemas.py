from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...modules.movies.schemas import Movie


RecommendationMode = Literal["content", "collaborative", "agent-ready"]


class RecommendationRequest(BaseModel):
    mode: RecommendationMode
    prompt: str = ""
    seedMovieName: str = ""
    userId: str = "1"
    topK: int = Field(default=6, ge=1, le=50)


class RecommendationItem(BaseModel):
    movie: Movie
    score: float
    reason: str
    source: str


class RecommendationResponse(BaseModel):
    items: list[RecommendationItem] = Field(default_factory=list)
