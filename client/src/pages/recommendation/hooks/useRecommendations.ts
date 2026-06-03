import { useEffect, useState } from "react";
import type { RecommendationItem, RecommendationRequest } from "../../../entities/movie/types";
import { getUserFacingApiMessage } from "../../../shared/api/errors";
import { recommendationApi } from "../api";

export function useRecommendations(request: RecommendationRequest | null) {
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!request) {
      setItems([]);
      setIsLoading(false);
      setErrorMessage(null);
      return;
    }

    let isActive = true;
    setIsLoading(true);
    setErrorMessage(null);

    void recommendationApi
      .recommend(request)
      .then((recommendations) => {
        if (isActive) {
          setItems(recommendations);
        }
      })
      .catch((error: unknown) => {
        if (isActive) {
          setItems([]);
          setErrorMessage(getUserFacingApiMessage(error));
        }
      })
      .finally(() => {
        if (isActive) {
          setIsLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [request]);

  return { items, isLoading, errorMessage };
}
