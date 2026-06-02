export type AtlasSummaryDto = {
  dataset?: string;
  movieCount?: number;
  movie_count?: number;
  userCount?: number;
  user_count?: number;
  ratingCount?: number;
  rating_count?: number;
  tagCount?: number;
  tag_count?: number;
  genreCount?: number;
  genre_count?: number;
  ratingMean?: number;
  rating_mean?: number;
};

export type GenreDistributionDto = {
  genre?: string;
  count?: number;
  movie_count?: number;
};

export type BudgetTrendDto = {
  year?: number;
  movie_year?: number;
  budget?: number;
  average_budget?: number;
};

export type RevenueBudgetDto = {
  title?: string;
  budget?: number;
  revenue?: number;
  popularity?: number;
  tmdb_popularity?: number;
};

export type CorrelationDto = {
  x?: string;
  y?: string;
  value?: number;
};
