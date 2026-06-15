from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RevenuePredictionRequest(BaseModel):
    movieName: str | None = Field(None, description="Movie name to search — if provided, looks up the movie from the dataset")
    features: dict[str, Any] | None = Field(None, description="Custom movie features for prediction. Omit fields to use median imputation.")


class FeatureSchemaItem(BaseModel):
    name: str
    label: str
    kind: str  # "numeric" | "categorical"
    defaultValue: Any = None
    options: list[str] | None = None  # for categorical features
    description: str = ""


class FeatureSchemaResponse(BaseModel):
    genres: list[str]
    languages: list[str]
    numericFields: list[FeatureSchemaItem]
    featureCount: int
    referenceYear: int


class EnsembleWeights(BaseModel):
    xgboost: float
    lightgbm: float


class ModelMetrics(BaseModel):
    rmseLog: float
    maeLog: float
    r2Log: float


class RevenuePredictionResponse(BaseModel):
    movieId: int | None = None
    movieName: str
    movieYear: int | None = None
    predictedRevenue: float
    predictedRevenueFormatted: str
    xgboostPredictedRevenue: float
    xgboostPredictedRevenueFormatted: str
    lightgbmPredictedRevenue: float
    lightgbmPredictedRevenueFormatted: str
    ensembleWeights: EnsembleWeights
    modelMetrics: ModelMetrics
    actualRevenue: float | None = None
    actualRevenueFormatted: str | None = None
    featureCount: int
