import { useEffect, useState } from "react";
import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  RevenueBudgetPoint,
} from "../../entities/movie/types";
import { cineScopeApi } from "../../shared/api";
import { getUserFacingApiMessage } from "../../shared/api/errors";

export type AtlasData = {
  summary: AtlasSummary;
  genres: GenreDistributionItem[];
  trend: BudgetTrendPoint[];
  points: RevenueBudgetPoint[];
  correlations: CorrelationCell[];
};

export function useAtlasData() {
  const [data, setData] = useState<AtlasData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    setErrorMessage(null);

    void Promise.all([
      cineScopeApi.getSummary(),
      cineScopeApi.getGenreDistribution(),
      cineScopeApi.getBudgetTrend(),
      cineScopeApi.getRevenueBudgetPoints(),
      cineScopeApi.getCorrelationCells(),
    ])
      .then(([summary, genres, trend, points, correlations]) => {
        if (isActive) {
          setData({ summary, genres, trend, points, correlations });
        }
      })
      .catch((error: unknown) => {
        if (isActive) {
          setData(null);
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
  }, []);

  return { data, isLoading, errorMessage };
}
