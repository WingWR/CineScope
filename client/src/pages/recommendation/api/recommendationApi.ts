import type { RecommendationItem, RecommendationRequest } from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";
import type { RecommendationRequestDto, RecommendationResponseDto } from "./recommendationDtos";
import { mapRecommendationList } from "./recommendationMappers";

export type RecommendationApi = {
  recommend(request: RecommendationRequest): Promise<RecommendationItem[]>;
};

export function createRecommendationApi(apiClient: ApiClient): RecommendationApi {
  return {
    async recommend(request: RecommendationRequest): Promise<RecommendationItem[]> {
      const response = await apiClient.post<RecommendationResponseDto>("/recommendations", toRecommendationRequestDto(request));
      return mapRecommendationList(response);
    },
  };
}

function toRecommendationRequestDto(request: RecommendationRequest): RecommendationRequestDto {
  return {
    mode: request.mode,
    prompt: request.prompt,
    seedMovieName: request.seedMovieName,
    userId: request.userId,
    topK: request.topK,
  };
}

export const recommendationApi = createRecommendationApi(backendApiClient);
