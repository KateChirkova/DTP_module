// моки fetch, router, localStorage для vitest
import { vi } from "vitest"

import { mockRouter } from "./mocks/next-navigation"

export { mockRouter }

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

export type FetchHandler = (
  url: string,
  init?: RequestInit,
) => Response | Promise<Response>

export function mockFetch(handlers: Record<string, FetchHandler>) {
  const impl = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString()
    for (const [fragment, handler] of Object.entries(handlers)) {
      if (url.includes(fragment)) {
        return handler(url, init)
      }
    }
    return jsonResponse({ error: "unmocked", url }, 404)
  })
  vi.stubGlobal("fetch", impl)
  return impl
}

export function seedSession(token = "test-token", user = "tester") {
  localStorage.setItem("token", token)
  localStorage.setItem("user", user)
}
