from __future__ import annotations

from fastapi import APIRouter, Depends

from server.app.modules.revenue.schemas import RevenuePredictionRequest, RevenuePredictionResponse
from server.app.modules.revenue.service import RevenueService, get_revenue_service


router = APIRouter(prefix="/revenue", tags=["revenue"])


@router.post("/predict", response_model=RevenuePredictionResponse)
def predict_revenue(
    request: RevenuePredictionRequest,
    service: RevenueService = Depends(get_revenue_service),
) -> RevenuePredictionResponse:
    return service.predict(request)
