from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MovieSort = Literal["popularity", "rating", "revenue", "year"]


class Movie(BaseModel):
    id: int | str
    title: str
    year: int | None = None
    genres: list[str] = Field(default_factory=list)
    ratingMean: float | None = None
    ratingCount: int | None = None
    tagCount: int | None = None
    tags: list[str] = Field(default_factory=list)
    overview: str | None = None
    runtimeMinutes: int | None = None
    tmdbPopularity: float | None = None
    budget: float | None = None
    revenue: float | None = None
    language: str | None = None
    posterUrl: str | None = None
    backdropUrl: str | None = None


class MovieListResponse(BaseModel):
    items: list[Movie] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    pageSize: int = 25
