import type { RecommendationItem } from "../../../entities/movie/types";

export type RecommendationResponse = {
  items: RecommendationItem[];
};
