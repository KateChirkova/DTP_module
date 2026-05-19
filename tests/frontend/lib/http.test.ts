// тесты apiUrl, apiFetch, 401 -> session expired
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { notifySessionExpired, setSessionExpiredHandler } from "@/lib/session-events"
import { apiFetch, apiUrl, bearerHeaders, wsNotificationsUrl } from "@/lib/http"
import { jsonResponse, mockFetch } from "../test-utils-fetch"

describe("http", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    setSessionExpiredHandler(null)
  })

  it("apiUrl нормализует путь", () => {
    expect(apiUrl("/api/v1/auth/login")).toContain("/api/v1/auth/login")
    expect(apiUrl("api/v1/x")).toContain("/api/v1/x")
  })

  it("wsNotificationsUrl кодирует token", () => {
    const url = wsNotificationsUrl("abc+token")
    expect(url).toMatch(/^ws:\/\//)
    expect(url).toContain("token=abc")
  })

  it("bearerHeaders добавляет Authorization", () => {
    expect(bearerHeaders("secret")).toEqual({ Authorization: "Bearer secret" })
  })

  it("apiFetch возвращает data при 200", async () => {
    mockFetch({
      "/notifications": () => jsonResponse({ success: true, total: 0 }),
    })
    const result = await apiFetch<{ success: boolean }>("/api/v1/notifications", {
      token: "t",
    })
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.data.success).toBe(true)
  })

  it("apiFetch при 401 вызывает onUnauthorized и notifySessionExpired", async () => {
    const onUnauthorized = vi.fn()
    const onExpired = vi.fn()
    setSessionExpiredHandler(onExpired)

    mockFetch({
      "/notifications": () => jsonResponse({}, 401),
    })

    const result = await apiFetch("/api/v1/notifications", {
      token: "bad",
      onUnauthorized,
    })

    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.status).toBe(401)
    expect(onUnauthorized).toHaveBeenCalledOnce()
    expect(onExpired).toHaveBeenCalledOnce()
  })

  it("apiFetch skipSessionExpired не вызывает notifySessionExpired", async () => {
    const onExpired = vi.fn()
    setSessionExpiredHandler(onExpired)

    mockFetch({
      "/auth/login": () => jsonResponse({}, 401),
    })

    await apiFetch("/api/v1/auth/login", { skipSessionExpired: true })
    expect(onExpired).not.toHaveBeenCalled()
  })

  it("apiFetch при 500 возвращает ok: false", async () => {
    mockFetch({
      "/x": () => jsonResponse({}, 500),
    })
    const result = await apiFetch("/api/v1/x")
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.status).toBe(500)
  })
})
