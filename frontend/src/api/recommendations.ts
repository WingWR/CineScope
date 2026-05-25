import { apiGet } from './client'
import type { MovieListItem } from '../types/api'

export function getRecommendations(movieId?: string | number) {
  const path = movieId ? `/recommendations/${movieId}` : '/recommendations'
  return apiGet<MovieListItem[]>(path)
}

