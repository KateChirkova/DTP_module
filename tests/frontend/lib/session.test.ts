// тесты verifySessionToken
import { describe, expect, it } from "vitest"

import { verifySessionToken } from "@/lib/session"
import { jsonResponse, mockFetch } from "../test-utils-fetch"

describe("verifySessionToken", () => {
  it("возвращает login при успешной verify", async () => {
    mockFetch({
      "/auth/verify": () => jsonResponse({ success: true, login: "operator1" }),
    })
    await expect(verifySessionToken("tok")).resolves.toBe("operator1")
  })

  it("возвращает null при 401", async () => {
    mockFetch({
      "/auth/verify": () => jsonResponse({}, 401),
    })
    await expect(verifySessionToken("bad")).resolves.toBeNull()
  })
})
