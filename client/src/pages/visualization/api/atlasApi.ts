import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  RevenueBudgetPoint,
} from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";

export type AtlasApi = {
  getSummary(): Promise<AtlasSummary>;
  getGenreDistribution(): Promise<GenreDistributionItem[]>;
  getBudgetTrend(): Promise<BudgetTrendPoint[]>;
  getRevenueBudgetPoints(): Promise<RevenueBudgetPoint[]>;
  getCorrelationCells(): Promise<CorrelationCell[]>;
};

export function createAtlasApi(apiClient: ApiClient): AtlasApi {
  return {
    getSummary(): Promise<AtlasSummary> {
      return apiClient.get<AtlasSummary>("/stats/summary");
    },

    getGenreDistribution(): Promise<GenreDistributionItem[]> {
      return apiClient.get<GenreDistributionItem[]>("/stats/genres");
    },

    getBudgetTrend(): Promise<BudgetTrendPoint[]> {
      return apiClient.get<BudgetTrendPoint[]>("/stats/budget-trend");
    },

    getRevenueBudgetPoints(): Promise<RevenueBudgetPoint[]> {
      return apiClient.get<RevenueBudgetPoint[]>("/stats/revenue-budget");
    },

    getCorrelationCells(): Promise<CorrelationCell[]> {
      return apiClient.get<CorrelationCell[]>("/stats/correlations");
    },
  };
}

export const atlasApi = createAtlasApi(backendApiClient);
