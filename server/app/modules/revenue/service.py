from __future__ import annotations

from ...core.errors import not_implemented
from ...modules.revenue.schemas import RevenuePredictionRequest, RevenuePredictionResponse


class RevenueService:
    def predict(self, request: RevenuePredictionRequest) -> RevenuePredictionResponse:
        not_implemented("revenue.service", "predict")


def get_revenue_service() -> RevenueService:
    return RevenueService()
