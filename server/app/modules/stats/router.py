from __future__ import annotations

from fastapi import APIRouter, Depends

from server.app.modules.stats.schemas import (
    AtlasSummary,
    BudgetTrendPoint,
    CorrelationCell,
    GenreDistributionItem,
    RevenueBudgetPoint,
)
from server.app.modules.stats.service import StatsService, get_stats_service


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=AtlasSummary)
def get_summary(service: StatsService = Depends(get_stats_service)) -> AtlasSummary:
    return service.get_summary()


@router.get("/genres", response_model=list[GenreDistributionItem])
def get_genres(service: StatsService = Depends(get_stats_service)) -> list[GenreDistributionItem]:
    return service.get_genres()


@router.get("/budget-trend", response_model=list[BudgetTrendPoint])
def get_budget_trend(service: StatsService = Depends(get_stats_service)) -> list[BudgetTrendPoint]:
    return service.get_budget_trend()


@router.get("/revenue-budget", response_model=list[RevenueBudgetPoint])
def get_revenue_budget(service: StatsService = Depends(get_stats_service)) -> list[RevenueBudgetPoint]:
    return service.get_revenue_budget()


@router.get("/correlations", response_model=list[CorrelationCell])
def get_correlations(service: StatsService = Depends(get_stats_service)) -> list[CorrelationCell]:
    return service.get_correlations()
