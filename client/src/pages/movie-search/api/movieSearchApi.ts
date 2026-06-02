import type { Movie, MovieFilters } from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";
import type { MovieListResponse } from "./movieSearchContracts";

export type MovieSearchApi = {
  listMovies(filters: MovieFilters): Promise<Movie[]>;
  getMovie(movieId: Movie["id"]): Promise<Movie>;
};

export function createMovieSearchApi(apiClient: ApiClient): MovieSearchApi {
  return {
    async listMovies(filters: MovieFilters): Promise<Movie[]> {
      const response = await apiClient.get<MovieListResponse>("/movies", {
        search: filters.search,
        genre: filters.genre,
        language: filters.language,
        minRating: filters.minRating,
        sort: filters.sort,
      });

      return response.items;
    },

    getMovie(movieId: Movie["id"]): Promise<Movie> {
      return apiClient.get<Movie>(`/movies/${encodeURIComponent(String(movieId))}`);
    },
  };
}

export const movieSearchApi = createMovieSearchApi(backendApiClient);
