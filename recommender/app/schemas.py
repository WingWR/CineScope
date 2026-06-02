from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    score: float
    reason: str
    source: str
    movie_year: float | None = None
    genres: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    query: dict[str, Any]
    count: int
    items: list[RecommendationItem]


class HealthResponse(BaseModel):
    service: str
    status: str
    artifacts_ready: bool
    missing_artifacts: list[str] = Field(default_factory=list)

