export type SortDirection = 'asc' | 'desc'

export type ApiErrorPayload = {
  message: string
  code?: string
  status?: number
}

export type PagedResult<T> = {
  items: T[]
  page: number
  pageSize: number
  total: number
}

export type MovieListParams = {
  query?: string
  genre?: string
  yearFrom?: number
  yearTo?: number
  sortBy?: 'weighted_rating' | 'rating_count' | 'tmdb_popularity' | 'tmdb_vote_average' | 'display_year'
  sortDirection?: SortDirection
  page?: number
  pageSize?: number
}

export type MovieListItem = {
  movieId: number
  displayTitle: string
  displayYear: number | null
  posterUrl: string | null
  genres: string[]
  ratingMean: number
  ratingCount: number
  weightedRating: number
  tmdbVoteAverage: number
  tmdbPopularity: number
  tmdbMediaType: 'movie' | 'tv'
}

export type MovieDetail = MovieListItem & {
  title: string
  tmdbId: number
  tmdbResolvedId: number
  overview: string | null
  backdropUrl: string | null
  runtimeMinutes: number | null
  releaseDate: string | null
  originalLanguage: string | null
  tmdbStatus: string | null
  tags: string[]
  tmdbGenres: string[]
}

export type GenreStat = {
  genre: string
  movieCount: number
}

export type DatasetSummary = {
  dataset: string
  scope: string
  movieCount: number
  userCount: number
  ratingCount: number
  tagCount: number
  genreCount: number
  ratingMean: number
  ratingMin: number
  ratingMax: number
  movieWithTmdbIdCount: number
  movieWithTmdbDetailCount: number
}

