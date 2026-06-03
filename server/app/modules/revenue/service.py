from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.revenue.schemas import RevenuePredictionRequest, RevenuePredictionResponse


class RevenueService:
    def predict(self, request: RevenuePredictionRequest) -> RevenuePredictionResponse:
        not_implemented("revenue.service", "predict")


def get_revenue_service() -> RevenueService:
    return RevenueService()
