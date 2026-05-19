import { API_BASE } from "@/lib/api"
import { logAppError } from "@/lib/app-log"
import { notifySessionExpired } from "@/lib/session-events"

// полный URL к эндпоинту API
export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`
  return `${API_BASE}${normalized}`
}

export function wsNotificationsUrl(token: string): string {
  const wsBase = API_BASE.replace(/^http/, "ws")
  return `${wsBase}/api/v1/ws/notifications?token=${encodeURIComponent(token)}`
}

export function bearerHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` }
}

type ApiFetchOptions = {
  token?: string
  method?: string
  body?: unknown
  onUnauthorized?: () => void
  skipSessionExpired?: boolean // true на /auth/login — не редиректить при 401
}

export async function apiFetch<T = unknown>(
  path: string,
  {
    token,
    method = "GET",
    body,
    onUnauthorized,
    skipSessionExpired = false,
  }: ApiFetchOptions = {},
): Promise<{ ok: true; data: T } | { ok: false; status: number }> {
  const headers: HeadersInit = {
    ...(token ? bearerHeaders(token) : {}),
    ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
  }

  const res = await fetch(apiUrl(path), {
    method,
    headers,
    cache: "no-store",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    onUnauthorized?.()
    if (!skipSessionExpired) {
      notifySessionExpired()
    }
    return { ok: false, status: 401 }
  }

  if (!res.ok) {
    if (res.status !== 401) {
      logAppError("apiFetch failed", { path, method, status: res.status })
    }
    return { ok: false, status: res.status }
  }

  const data = (await res.json()) as T
  return { ok: true, data }
}
