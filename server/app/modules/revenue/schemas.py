from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RevenuePredictionRequest(BaseModel):
    movieId: int | str | None = None
    features: dict[str, Any] = Field(default_factory=dict)


class RevenuePredictionResponse(BaseModel):
    movieId: int | str | None = None
    predictedRevenue: float
    model: str
