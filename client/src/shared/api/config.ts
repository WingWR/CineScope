export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);
export const API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 8000);

function normalizeBaseUrl(value: string | undefined): string {
  return value?.trim().replace(/\/$/, "") ?? "";
}
