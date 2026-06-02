import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  Movie,
  MovieFilters,
  RecommendationItem,
  RecommendationRequest,
  RevenueBudgetPoint,
} from "../../entities/movie/types";

export type MovieRepository = {
  listMovies(filters: MovieFilters): Promise<Movie[]>;
  getMovie(movieId: Movie["id"]): Promise<Movie | undefined>;
};

export type RecommendationRepository = {
  recommend(request: RecommendationRequest): Promise<RecommendationItem[]>;
};

export type AtlasRepository = {
  getSummary(): Promise<AtlasSummary>;
  getGenreDistribution(): Promise<GenreDistributionItem[]>;
  getBudgetTrend(): Promise<BudgetTrendPoint[]>;
  getRevenueBudgetPoints(): Promise<RevenueBudgetPoint[]>;
  getCorrelationCells(): Promise<CorrelationCell[]>;
};

export type CineScopeApi = MovieRepository & RecommendationRepository & AtlasRepository;
