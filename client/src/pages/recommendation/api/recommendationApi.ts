import type { RecommendationItem, RecommendationRequest } from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";
import type { RecommendationResponse } from "./recommendationContracts";

export type RecommendationApi = {
  recommend(request: RecommendationRequest): Promise<RecommendationItem[]>;
};

export function createRecommendationApi(apiClient: ApiClient): RecommendationApi {
  return {
    async recommend(request: RecommendationRequest): Promise<RecommendationItem[]> {
      const response = await apiClient.post<RecommendationResponse>("/recommendations", request);
      return response.items;
    },
  };
}

export const recommendationApi = createRecommendationApi(backendApiClient);
