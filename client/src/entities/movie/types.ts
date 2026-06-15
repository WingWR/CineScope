export type Movie = {
  id: number | string;
  title: string;
  year?: number;
  genres?: string[];
  ratingMean?: number;
  ratingCount?: number;
  tagCount?: number;
  tags?: string[];
  overview?: string;
  runtimeMinutes?: number;
  tmdbPopularity?: number;
  budget?: number;
  revenue?: number;
  language?: string;
  posterUrl?: string;
  backdropUrl?: string;
};

export type MovieSort = "popularity" | "rating" | "revenue" | "year";

export type MovieFilters = {
  search: string;
  genre?: string;
  language?: string;
  minRating?: number;
  sort?: MovieSort;
  page?: number;
  pageSize?: number;
};

export type RecommendationMode = "content" | "collaborative" | "agent-ready";

export type RecommendationRequest = {
  mode: RecommendationMode;
  prompt: string;
  seedMovieName: string;
  userId: string;
  topK: number;
};

export type RecommendationItem = {
  movie: Movie;
  score: number;
  reason: string;
  source: "content" | "collaborative" | "hybrid" | "agent-ready" | string;
};

export type AtlasSummary = {
  dataset?: string;
  movieCount?: number;
  userCount?: number;
  ratingCount?: number;
  tagCount?: number;
  genreCount?: number;
  ratingMean?: number;
};

export type GenreDistributionItem = {
  genre: string;
  count: number;
};

export type BudgetTrendPoint = {
  year: number;
  budget: number;
};

export type RevenueBudgetPoint = {
  title: string;
  budget: number;
  revenue: number;
  popularity?: number;
};

export type CorrelationCell = {
  x: string;
  y: string;
  value: number;
};

export type RevenuePredictionRequest = {
  movieName?: string;
  features?: Record<string, unknown>;
};

export type FeatureSchemaItem = {
  name: string;
  label: string;
  kind: "numeric" | "categorical";
  defaultValue: unknown;
  options: string[] | null;
  description: string;
};

export type FeatureSchemaResponse = {
  genres: string[];
  languages: string[];
  numericFields: FeatureSchemaItem[];
  featureCount: number;
  referenceYear: number;
};

export type EnsembleWeights = {
  xgboost: number;
  lightgbm: number;
};

export type ModelMetrics = {
  rmseLog: number;
  maeLog: number;
  r2Log: number;
};

export type RevenuePredictionResponse = {
  movieId: number | null;
  movieName: string;
  movieYear: number | null;
  predictedRevenue: number;
  predictedRevenueFormatted: string;
  xgboostPredictedRevenue: number;
  xgboostPredictedRevenueFormatted: string;
  lightgbmPredictedRevenue: number;
  lightgbmPredictedRevenueFormatted: string;
  ensembleWeights: EnsembleWeights;
  modelMetrics: ModelMetrics;
  actualRevenue: number | null;
  actualRevenueFormatted: string | null;
  featureCount: number;
};
