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
