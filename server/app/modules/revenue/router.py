from __future__ import annotations

from fastapi import APIRouter, Depends

from ...modules.revenue.schemas import (
    FeatureSchemaResponse,
    RevenuePredictionRequest,
    RevenuePredictionResponse,
)
from ...modules.revenue.service import RevenueService, get_revenue_service


router = APIRouter(prefix="/revenue", tags=["revenue"])


@router.get("/schema", response_model=FeatureSchemaResponse)
def get_schema(service: RevenueService = Depends(get_revenue_service)) -> FeatureSchemaResponse:
    """Return the feature schema used by the revenue prediction model (genres, languages, numeric fields, medians)."""
    return service.get_schema()


@router.post("/predict", response_model=RevenuePredictionResponse)
def predict_revenue(
    request: RevenuePredictionRequest,
    service: RevenueService = Depends(get_revenue_service),
) -> RevenuePredictionResponse:
    """Predict box-office revenue. Provide either `movieName` to look up a movie, or `features` dict with custom values."""
    return service.predict(request)
