import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  RevenueBudgetPoint,
} from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";
import type {
  AtlasSummaryDto,
  BudgetTrendDto,
  CorrelationDto,
  GenreDistributionDto,
  RevenueBudgetDto,
} from "./atlasDtos";
import {
  mapAtlasSummary,
  mapBudgetTrend,
  mapCorrelations,
  mapGenreDistribution,
  mapRevenueBudget,
} from "./atlasMappers";

export type AtlasApi = {
  getSummary(): Promise<AtlasSummary>;
  getGenreDistribution(): Promise<GenreDistributionItem[]>;
  getBudgetTrend(): Promise<BudgetTrendPoint[]>;
  getRevenueBudgetPoints(): Promise<RevenueBudgetPoint[]>;
  getCorrelationCells(): Promise<CorrelationCell[]>;
};

export function createAtlasApi(apiClient: ApiClient): AtlasApi {
  return {
    async getSummary(): Promise<AtlasSummary> {
      const response = await apiClient.get<AtlasSummaryDto>("/stats/summary");
      return mapAtlasSummary(response);
    },

    async getGenreDistribution(): Promise<GenreDistributionItem[]> {
      const response = await apiClient.get<GenreDistributionDto[]>("/stats/genres");
      return mapGenreDistribution(response);
    },

    async getBudgetTrend(): Promise<BudgetTrendPoint[]> {
      const response = await apiClient.get<BudgetTrendDto[]>("/stats/budget-trend");
      return mapBudgetTrend(response);
    },

    async getRevenueBudgetPoints(): Promise<RevenueBudgetPoint[]> {
      const response = await apiClient.get<RevenueBudgetDto[]>("/stats/revenue-budget");
      return mapRevenueBudget(response);
    },

    async getCorrelationCells(): Promise<CorrelationCell[]> {
      const response = await apiClient.get<CorrelationDto[]>("/stats/correlations");
      return mapCorrelations(response);
    },
  };
}

export const atlasApi = createAtlasApi(backendApiClient);
