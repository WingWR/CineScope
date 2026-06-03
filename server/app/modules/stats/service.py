from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.stats.repository import StatsRepository
from server.app.modules.stats.schemas import (
    AtlasSummary,
    BudgetTrendPoint,
    CorrelationCell,
    GenreDistributionItem,
    RevenueBudgetPoint,
)


class StatsService:
    def __init__(self, repository: StatsRepository | None = None) -> None:
        self.repository = repository or StatsRepository()

    def get_summary(self) -> AtlasSummary:
        not_implemented("stats.service", "get_summary")

    def get_genres(self) -> list[GenreDistributionItem]:
        not_implemented("stats.service", "get_genres")

    def get_budget_trend(self) -> list[BudgetTrendPoint]:
        not_implemented("stats.service", "get_budget_trend")

    def get_revenue_budget(self) -> list[RevenueBudgetPoint]:
        not_implemented("stats.service", "get_revenue_budget")

    def get_correlations(self) -> list[CorrelationCell]:
        not_implemented("stats.service", "get_correlations")


def get_stats_service() -> StatsService:
    return StatsService()
