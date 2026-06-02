import type { RecommendationMode } from "../../../entities/movie/types";

export type RecommendationRequestDto = {
  mode: RecommendationMode;
  prompt?: string;
  seedMovieName?: string;
  userId?: string;
  topK?: number;
};

export type RecommendationMovieDto = {
  id?: number | string;
  movie_id?: number | string;
  title?: string;
  title_clean?: string;
  year?: number | string;
  movie_year?: number | string;
  genres?: string[];
  genres_json?: string;
  ratingMean?: number | string;
  rating_mean?: number | string;
  posterUrl?: string;
  poster_url?: string;
};

export type RecommendationItemDto = {
  movie?: RecommendationMovieDto;
  movie_id?: number | string;
  title?: string;
  score?: number | string;
  reason?: string;
  source?: string;
  movie_year?: number | string;
  genres?: string[];
};

export type RecommendationResponseDto =
  | RecommendationItemDto[]
  | {
      query?: Record<string, unknown>;
      count?: number;
      items: RecommendationItemDto[];
    };
