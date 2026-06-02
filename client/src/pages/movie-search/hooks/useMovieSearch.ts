import { useEffect, useMemo, useState } from "react";
import type { Movie, MovieFilters } from "../../../entities/movie/types";
import { getUserFacingApiMessage } from "../../../shared/api/errors";
import { movieSearchApi } from "../api";

type MovieSearchState = {
  movies: Movie[];
  isLoading: boolean;
  errorMessage: string | null;
};

export function useMovieSearch(filters: MovieFilters) {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const stableFilters = useMemo(
    () => filters,
    [filters.genre, filters.language, filters.minRating, filters.search, filters.sort],
  );

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    setErrorMessage(null);

    void movieSearchApi
      .listMovies(stableFilters)
      .then((items) => {
        if (isActive) {
          setMovies(items);
        }
      })
      .catch((error: unknown) => {
        if (isActive) {
          setMovies([]);
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

  return { movies, isLoading, errorMessage } satisfies MovieSearchState;
}
