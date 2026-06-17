import type { Movie } from "../../../entities/movie/types";

export type MovieListResponse = {
  items: Movie[];
  total: number;
  page: number;
  pageSize: number;
};
