// тесты notifySessionExpired
import { describe, expect, it, vi } from "vitest"

import { notifySessionExpired, setSessionExpiredHandler } from "@/lib/session-events"

describe("session-events", () => {
  it("notifySessionExpired вызывает зарегистрированный handler", () => {
    const handler = vi.fn()
    setSessionExpiredHandler(handler)
    notifySessionExpired()
    expect(handler).toHaveBeenCalledOnce()
    setSessionExpiredHandler(null)
  })

  it("notifySessionExpired без handler не падает", () => {
    setSessionExpiredHandler(null)
    expect(() => notifySessionExpired()).not.toThrow()
  })
})
