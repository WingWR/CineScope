export class ApiUnavailableError extends Error {
  readonly code = "API_UNAVAILABLE";

  constructor(message = "Backend API is not configured yet.") {
    super(message);
    this.name = "ApiUnavailableError";
  }
}

export class ApiResponseError extends Error {
  readonly code = "API_RESPONSE_ERROR";

  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiResponseError";
  }
}

export function getUserFacingApiMessage(error: unknown): string {
  if (error instanceof ApiUnavailableError) {
    return "Backend API is not configured. Set VITE_API_BASE_URL and the page will request real data.";
  }

  if (error instanceof ApiResponseError) {
    return `The API did not return usable data${error.status ? ` (HTTP ${error.status})` : ""}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "No backend response was received.";
}
