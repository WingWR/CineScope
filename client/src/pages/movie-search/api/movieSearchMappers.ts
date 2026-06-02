import type { Movie } from "../../../entities/movie/types";
import type { MovieDto, MovieListDto } from "./movieSearchDtos";

export function mapMovieList(response: MovieListDto): Movie[] {
  const items = Array.isArray(response) ? response : response.items;
  return items.map(mapMovie);
}

export function mapMovie(dto: MovieDto): Movie {
  const title = dto.title ?? dto.title_clean ?? "Untitled";

  return {
    id: dto.id ?? dto.movie_id ?? title,
    title,
    year: toOptionalNumber(dto.year ?? dto.movie_year),
    genres: toStringArray(dto.genres, dto.genres_json),
    ratingMean: toOptionalNumber(dto.ratingMean ?? dto.rating_mean),
    ratingCount: toOptionalNumber(dto.ratingCount ?? dto.rating_count),
    tagCount: toOptionalNumber(dto.tagCount ?? dto.tag_count),
    tags: toStringArray(dto.tags, dto.top_tags_json),
    overview: dto.overview,
    runtimeMinutes: toOptionalNumber(dto.runtimeMinutes ?? dto.runtime_minutes),
    tmdbPopularity: toOptionalNumber(dto.tmdbPopularity ?? dto.tmdb_popularity),
    budget: toOptionalNumber(dto.budget),
    revenue: toOptionalNumber(dto.revenue),
    language: dto.language ?? dto.original_language,
    posterUrl: dto.posterUrl ?? dto.poster_url,
    backdropUrl: dto.backdropUrl ?? dto.backdrop_url,
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
