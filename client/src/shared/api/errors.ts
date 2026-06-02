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
    return "后端接口尚未配置。设置 VITE_API_BASE_URL 后，页面会自动请求真实接口。";
  }

  if (error instanceof ApiResponseError) {
    return `接口暂时没有返回可用数据${error.status ? `（HTTP ${error.status}）` : ""}。`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "未收到后端响应，请稍后重试。";
}
