from __future__ import annotations

from fastapi import APIRouter, Depends

from server.app.modules.recommendations.schemas import RecommendationRequest, RecommendationResponse
from server.app.modules.recommendations.service import RecommendationService, get_recommendation_service


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def recommend(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    return service.recommend(request)
