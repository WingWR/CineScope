import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  RevenueBudgetPoint,
} from "../../../entities/movie/types";
import type {
  AtlasSummaryDto,
  BudgetTrendDto,
  CorrelationDto,
  GenreDistributionDto,
  RevenueBudgetDto,
} from "./atlasDtos";

export function mapAtlasSummary(dto: AtlasSummaryDto): AtlasSummary {
  return {
    dataset: dto.dataset,
    movieCount: dto.movieCount ?? dto.movie_count,
    userCount: dto.userCount ?? dto.user_count,
    ratingCount: dto.ratingCount ?? dto.rating_count,
    tagCount: dto.tagCount ?? dto.tag_count,
    genreCount: dto.genreCount ?? dto.genre_count,
    ratingMean: dto.ratingMean ?? dto.rating_mean,
  };
}

export function mapGenreDistribution(items: GenreDistributionDto[]): GenreDistributionItem[] {
  return items.map((item) => ({
    genre: item.genre ?? "Unknown",
    count: item.count ?? item.movie_count ?? 0,
  }));
}

export function mapBudgetTrend(items: BudgetTrendDto[]): BudgetTrendPoint[] {
  return items.flatMap((item) => {
    const year = item.year ?? item.movie_year;
    const budget = item.budget ?? item.average_budget;
    return typeof year === "number" && typeof budget === "number" ? [{ year, budget }] : [];
  });
}

export function mapRevenueBudget(items: RevenueBudgetDto[]): RevenueBudgetPoint[] {
  return items.flatMap((item) => {
    if (typeof item.budget !== "number" || typeof item.revenue !== "number") {
      return [];
    }

    return [
      {
        title: item.title ?? "Untitled",
        budget: item.budget,
        revenue: item.revenue,
        popularity: item.popularity ?? item.tmdb_popularity,
      },
    ];
  });
}

export function mapCorrelations(items: CorrelationDto[]): CorrelationCell[] {
  return items.flatMap((item) => {
    if (!item.x || !item.y || typeof item.value !== "number") {
      return [];
    }

    return [{ x: item.x, y: item.y, value: item.value }];
  });
}
