import { apiGet } from './client'
import type { DatasetSummary, GenreStat } from '../types/api'

export function getDatasetSummary() {
  return apiGet<DatasetSummary>('/stats/summary')
}

export function getGenreStats() {
  return apiGet<GenreStat[]>('/stats/genres')
}

