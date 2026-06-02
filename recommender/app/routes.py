from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, HTTPException, Query

from recommender.app.schemas import HealthResponse, RecommendationResponse
from recommender.app.settings import (
    COLLABORATIVE_ARTIFACT_DIR,
    CONTENT_ARTIFACT_DIR,
    DEFAULT_NEIGHBOR_K,
    DEFAULT_TOP_K,
    RECOMMENDER_SERVICE_NAME,
)
from recommender.core.exceptions import ArtifactsMissingError, MovieNotFoundError, UserNotFoundError
from recommender.core.service import RecommenderService


router = APIRouter()


@lru_cache(maxsize=1)
def get_service() -> RecommenderService:
    return RecommenderService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    missing = _missing_artifacts()
    return HealthResponse(
        service=RECOMMENDER_SERVICE_NAME,
        status="ok" if not missing else "artifacts_missing",
        artifacts_ready=not missing,
        missing_artifacts=[str(path) for path in missing],
    )


@router.get("/recommend/content", response_model=RecommendationResponse)
def recommend_content(
    movie_name: str = Query(..., min_length=1),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=50),
) -> RecommendationResponse:
    try:
        return get_service().recommend_by_content(movie_name=movie_name, top_k=top_k)
    except MovieNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArtifactsMissingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/recommend/collaborative", response_model=RecommendationResponse)
def recommend_collaborative(
    user_id: int = Query(..., ge=1),
    movie_name: str | None = Query(None, min_length=1),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=50),
    neighbor_k: int = Query(DEFAULT_NEIGHBOR_K, ge=1, le=100),
) -> RecommendationResponse:
    try:
        return get_service().recommend_by_collaborative(
            user_id=user_id,
            movie_name=movie_name,
            top_k=top_k,
            neighbor_k=neighbor_k,
        )
    except (MovieNotFoundError, UserNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArtifactsMissingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _missing_artifacts() -> list[object]:
    required = [
        CONTENT_ARTIFACT_DIR / "overview_tfidf.joblib",
        CONTENT_ARTIFACT_DIR / "overview_matrix.npz",
        CONTENT_ARTIFACT_DIR / "content_count.joblib",
        CONTENT_ARTIFACT_DIR / "content_matrix.npz",
        CONTENT_ARTIFACT_DIR / "movie_index.json",
        COLLABORATIVE_ARTIFACT_DIR / "movie_user_matrix.npz",
        COLLABORATIVE_ARTIFACT_DIR / "user_movie_matrix.npz",
        COLLABORATIVE_ARTIFACT_DIR / "movie_knn.joblib",
        COLLABORATIVE_ARTIFACT_DIR / "user_knn.joblib",
        COLLABORATIVE_ARTIFACT_DIR / "movie_index.json",
        COLLABORATIVE_ARTIFACT_DIR / "user_index.json",
    ]
    return [path for path in required if not path.exists()]

