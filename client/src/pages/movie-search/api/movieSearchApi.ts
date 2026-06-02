import type { Movie, MovieFilters } from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";
import type { MovieDto, MovieListDto } from "./movieSearchDtos";
import { mapMovie, mapMovieList } from "./movieSearchMappers";

export type MovieSearchApi = {
  listMovies(filters: MovieFilters): Promise<Movie[]>;
  getMovie(movieId: Movie["id"]): Promise<Movie | undefined>;
};

export function createMovieSearchApi(apiClient: ApiClient): MovieSearchApi {
  return {
    async listMovies(filters: MovieFilters): Promise<Movie[]> {
      const response = await apiClient.get<MovieListDto>("/movies", {
        search: filters.search,
        genre: filters.genre,
        language: filters.language,
        minRating: filters.minRating,
        sort: filters.sort,
      });

      return mapMovieList(response);
    },

    async getMovie(movieId: Movie["id"]): Promise<Movie | undefined> {
      const response = await apiClient.get<MovieDto>(`/movies/${encodeURIComponent(String(movieId))}`);
      return mapMovie(response);
    },
  };
}

export const movieSearchApi = createMovieSearchApi(backendApiClient);
