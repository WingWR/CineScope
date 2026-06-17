from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RagSource(BaseModel):
    id: str
    name: str
    path: str
    type: str


class RagIndexRequest(BaseModel):
    sourceNames: list[str] | None = None
    rebuild: bool = False


class RagIndexResponse(BaseModel):
    indexedCount: int
    sources: list[RagSource] = Field(default_factory=list)


class RagSearchRequest(BaseModel):
    query: str
    topK: int = Field(default=6, ge=1, le=20)


class RagSearchResult(BaseModel):
    source: RagSource
    title: str | None = None
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchResponse(BaseModel):
    items: list[RagSearchResult] = Field(default_factory=list)
