import type { ApiErrorPayload } from '../types/api'

export class ApiConfigurationError extends Error {
  constructor() {
    super('VITE_API_BASE_URL is not configured')
    this.name = 'ApiConfigurationError'
  }
}

export class ApiRequestError extends Error {
  readonly status: number
  readonly payload: ApiErrorPayload | null

  constructor(status: number, payload: ApiErrorPayload | null) {
    super(payload?.message ?? `API request failed with status ${status}`)
    this.name = 'ApiRequestError'
    this.status = status
    this.payload = payload
  }
}

export function isApiConfigured() {
  return Boolean(import.meta.env.VITE_API_BASE_URL)
}

function apiUrl(path: string, searchParams?: URLSearchParams) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL
  if (!baseUrl) {
    throw new ApiConfigurationError()
  }
  const url = new URL(path, baseUrl)
  if (searchParams) {
    url.search = searchParams.toString()
  }
  return url
}

export async function apiGet<T>(path: string, searchParams?: URLSearchParams): Promise<T> {
  const response = await fetch(apiUrl(path, searchParams), {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    let payload: ApiErrorPayload | null = null
    try {
      payload = await response.json()
    } catch {
      // Non-JSON error bodies are still represented by status code below.
    }
    throw new ApiRequestError(response.status, payload)
  }

  return response.json() as Promise<T>
}
