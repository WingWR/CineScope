import type {
  FeatureSchemaResponse,
  RevenuePredictionRequest,
  RevenuePredictionResponse,
} from "../../../entities/movie/types";
import { backendApiClient } from "../../../shared/api";
import type { ApiClient } from "../../../shared/api/client";

export type RevenuePredictionApi = {
  getSchema(): Promise<FeatureSchemaResponse>;
  predict(request: RevenuePredictionRequest): Promise<RevenuePredictionResponse>;
};

export function createRevenuePredictionApi(apiClient: ApiClient): RevenuePredictionApi {
  return {
    getSchema(): Promise<FeatureSchemaResponse> {
      return apiClient.get<FeatureSchemaResponse>("/revenue/schema");
    },

    predict(request: RevenuePredictionRequest): Promise<RevenuePredictionResponse> {
      return apiClient.post<RevenuePredictionResponse>("/revenue/predict", request);
    },
  };
}

export const revenuePredictionApi = createRevenuePredictionApi(backendApiClient);
