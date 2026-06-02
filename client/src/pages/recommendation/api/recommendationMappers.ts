import type { Movie, RecommendationItem } from "../../../entities/movie/types";
import type {
  RecommendationItemDto,
  RecommendationMovieDto,
  RecommendationResponseDto,
} from "./recommendationDtos";

export function mapRecommendationList(response: RecommendationResponseDto): RecommendationItem[] {
  const items = Array.isArray(response) ? response : response.items;
  return items.map(mapRecommendationItem);
}

function mapRecommendationItem(dto: RecommendationItemDto): RecommendationItem {
  const movie = dto.movie
    ? mapRecommendationMovie(dto.movie)
    : mapRecommendationMovie({
        movie_id: dto.movie_id,
        title: dto.title,
        movie_year: dto.movie_year,
        genres: dto.genres,
      });

  return {
    movie,
    score: toOptionalNumber(dto.score) ?? 0,
    reason: dto.reason ?? "No explanation returned.",
    source: dto.source ?? "backend",
  };
}

function mapRecommendationMovie(dto: RecommendationMovieDto): Movie {
  const title = dto.title ?? dto.title_clean ?? "Untitled";

  return {
    id: dto.id ?? dto.movie_id ?? title,
    title,
    year: toOptionalNumber(dto.year ?? dto.movie_year),
    genres: toStringArray(dto.genres, dto.genres_json),
    ratingMean: toOptionalNumber(dto.ratingMean ?? dto.rating_mean),
    posterUrl: dto.posterUrl ?? dto.poster_url,
  };
}

function toOptionalNumber(value: number | string | undefined): number | undefined {
  if (value === undefined || value === "") {
    return undefined;
  }

  const number = Number(value);
  return Number.isFinite(number) ? number : undefined;
}

function toStringArray(value: string[] | undefined, jsonValue?: string): string[] | undefined {
  if (Array.isArray(value)) {
    return value;
  }

  if (!jsonValue) {
    return undefined;
  }

  try {
    const parsed = JSON.parse(jsonValue) as unknown;
    return Array.isArray(parsed) ? parsed.map(String) : undefined;
  } catch {
    return undefined;
  }
}
