import { API_TIMEOUT_MS } from "./config";
import { ApiResponseError, ApiUnavailableError } from "./errors";

type JsonPrimitive = string | number | boolean | null;
type QueryValue = JsonPrimitive | undefined;
export type QueryParams = Record<string, QueryValue>;

export class ApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly label: string,
  ) {}

  isConfigured(): boolean {
    return this.baseUrl.length > 0;
  }

  get<T>(path: string, params?: QueryParams): Promise<T> {
    return this.request<T>(`${path}${toQueryString(params)}`);
  }

  post<T>(path: string, payload: unknown): Promise<T> {
    return this.request<T>(path, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    if (!this.baseUrl) {
      throw new ApiUnavailableError(`${this.label} is not configured.`);
    }

    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS);

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...init.headers,
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new ApiResponseError(`${this.label} returned an unsuccessful response.`, response.status);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      return (await response.json()) as T;
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        throw new ApiResponseError(`${this.label} timed out before responding.`);
      }

      throw error;
    } finally {
      window.clearTimeout(timeout);
    }
  }
}

export function toQueryString(params?: QueryParams): string {
  if (!params) {
    return "";
  }

  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      searchParams.set(key, String(value));
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}
