import { apiGet } from './client'
import type { MovieDetail, MovieListItem, MovieListParams, PagedResult } from '../types/api'

function movieListSearchParams(params: MovieListParams) {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, String(value))
    }
  })
  return searchParams
}

export function getMovieList(params: MovieListParams = {}) {
  return apiGet<PagedResult<MovieListItem>>('/movies', movieListSearchParams(params))
}

export function getMovieDetail(movieId: string | number) {
  return apiGet<MovieDetail>(`/movies/${movieId}`)
}

export function getTopRatedMovies() {
  return apiGet<MovieListItem[]>('/movies/top-rated')
}

export function getPopularMovies() {
  return apiGet<MovieListItem[]>('/movies/popular')
}

