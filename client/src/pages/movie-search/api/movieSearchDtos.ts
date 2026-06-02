import type { MovieSort } from "../../../entities/movie/types";

export type MovieDto = {
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
  ratingCount?: number | string;
  rating_count?: number | string;
  tagCount?: number | string;
  tag_count?: number | string;
  tags?: string[];
  top_tags_json?: string;
  overview?: string;
  runtimeMinutes?: number | string;
  runtime_minutes?: number | string;
  tmdbPopularity?: number | string;
  tmdb_popularity?: number | string;
  budget?: number | string;
  revenue?: number | string;
  language?: string;
  original_language?: string;
  posterUrl?: string;
  poster_url?: string;
  backdropUrl?: string;
  backdrop_url?: string;
};

export type MovieListDto = MovieDto[] | { items: MovieDto[]; count?: number };

export type MovieFiltersDto = {
  search?: string;
  genre?: string;
  language?: string;
  minRating?: number;
  sort?: MovieSort;
};
