from __future__ import annotations

from pydantic import BaseModel


class AtlasSummary(BaseModel):
    dataset: str | None = None
    movieCount: int | None = None
    userCount: int | None = None
    ratingCount: int | None = None
    tagCount: int | None = None
    genreCount: int | None = None
    ratingMean: float | None = None


class GenreDistributionItem(BaseModel):
    genre: str
    count: int


class BudgetTrendPoint(BaseModel):
    year: int
    budget: float


class RevenueBudgetPoint(BaseModel):
    title: str
    budget: float
    revenue: float
    popularity: float | None = None


class CorrelationCell(BaseModel):
    x: str
    y: str
    value: float
