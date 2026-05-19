// тесты parseBackendDateAsUtc и форматирования Москва
import { describe, expect, it } from "vitest"

import {
  formatDateMoscow,
  formatTimeMoscow,
  parseBackendDateAsUtc,
} from "@/lib/datetime"

describe("datetime", () => {
  it("parseBackendDateAsUtc понимает ISO с Z", () => {
    const d = parseBackendDateAsUtc("2024-06-15T12:30:00Z")
    expect(d).not.toBeNull()
    expect(d!.toISOString()).toBe("2024-06-15T12:30:00.000Z")
  })

  it("parseBackendDateAsUtc добавляет Z к naive datetime", () => {
    const d = parseBackendDateAsUtc("2024-06-15 12:30:00")
    expect(d).not.toBeNull()
    expect(d!.toISOString()).toBe("2024-06-15T12:30:00.000Z")
  })

  it("parseBackendDateAsUtc возвращает null для пустого", () => {
    expect(parseBackendDateAsUtc(null)).toBeNull()
    expect(parseBackendDateAsUtc("")).toBeNull()
  })

  it("formatTimeMoscow форматирует в Europe/Moscow", () => {
    const t = formatTimeMoscow("2024-06-15T09:00:00Z")
    expect(t).toMatch(/^\d{2}:\d{2}$/)
  })

  it("formatTimeMoscow использует fallback", () => {
    expect(formatTimeMoscow(null, "—")).toBe("—")
  })

  it("formatDateMoscow возвращает дату", () => {
    const d = formatDateMoscow("2024-06-15T12:00:00Z")
    expect(d.length).toBeGreaterThan(0)
  })
})
