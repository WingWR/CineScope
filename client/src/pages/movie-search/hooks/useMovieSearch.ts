import { useEffect, useMemo, useState } from "react";
import type { Movie, MovieFilters } from "../../../entities/movie/types";
import { getUserFacingApiMessage } from "../../../shared/api/errors";
import { movieSearchApi } from "../api";

type MovieSearchState = {
  movies: Movie[];
  page: number;
  pageSize: number;
  total: number;
  isLoading: boolean;
  errorMessage: string | null;
};

export function useMovieSearch(filters: MovieFilters) {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [page, setPage] = useState(filters.page ?? 1);
  const [pageSize, setPageSize] = useState(filters.pageSize ?? 25);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const stableFilters = useMemo(
    () => filters,
    [filters.genre, filters.language, filters.minRating, filters.page, filters.pageSize, filters.search, filters.sort],
  );

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    setErrorMessage(null);

    void movieSearchApi
      .listMovies(stableFilters)
      .then((response) => {
        if (isActive) {
          setMovies(response.items);
          setPage(response.page);
          setPageSize(response.pageSize);
          setTotal(response.total);
        }
      })
      .catch((error: unknown) => {
        if (isActive) {
          setMovies([]);
          setTotal(0);
          setErrorMessage(getUserFacingApiMessage(error));
        }
      })
      .finally(() => {
        if (isActive) {
          setIsLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [stableFilters]);

  return { movies, page, pageSize, total, isLoading, errorMessage } satisfies MovieSearchState;
}
