import type {
  AtlasSummary,
  BudgetTrendPoint,
  CorrelationCell,
  GenreDistributionItem,
  Movie,
  MovieFilters,
  RecommendationItem,
  RecommendationRequest,
  RevenueBudgetPoint,
} from "../../entities/movie/types";
import { ApiResponseError, ApiUnavailableError } from "./errors";
import type { CineScopeApi } from "./ports";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
const DEFAULT_TIMEOUT_MS = 8000;

export const httpApi: CineScopeApi = {
  listMovies(filters: MovieFilters) {
    return request<Movie[]>(`/movies${toQueryString(filters)}`);
  },

  getMovie(movieId: Movie["id"]) {
    return request<Movie>(`/movies/${encodeURIComponent(String(movieId))}`);
  },

  recommend(payload: RecommendationRequest) {
    return request<RecommendationItem[]>("/recommendations", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getSummary() {
    return request<AtlasSummary>("/stats/summary");
  },

  getGenreDistribution() {
    return request<GenreDistributionItem[]>("/stats/genres");
  },

  getBudgetTrend() {
    return request<BudgetTrendPoint[]>("/stats/budget-trend");
  },

  getRevenueBudgetPoints() {
    return request<RevenueBudgetPoint[]>("/stats/revenue-budget");
  },

  getCorrelationCells() {
    return request<CorrelationCell[]>("/stats/correlations");
  },
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!API_BASE_URL) {
    throw new ApiUnavailableError();
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new ApiResponseError("Backend returned an unsuccessful response.", response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiResponseError("Request timed out before the backend responded.");
    }

    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function toQueryString(filters: MovieFilters): string {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      params.set(key, String(value));
    }
  });

  const query = params.toString();
  return query ? `?${query}` : "";
}
