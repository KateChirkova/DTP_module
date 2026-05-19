// тесты localStorage и cookie dtp_auth
import { beforeEach, describe, expect, it } from "vitest"

import { clearAuthCookie, setAuthCookie } from "@/lib/auth-cookie"
import { clearStorage, readStorage, writeStorage } from "@/lib/storage"

describe("storage", () => {
  beforeEach(() => {
    localStorage.clear()
    document.cookie = ""
  })

  it("writeStorage и readStorage", () => {
    writeStorage("token", "abc")
    expect(readStorage("token")).toBe("abc")
  })

  it("clearStorage очищает localStorage", () => {
    writeStorage("token", "x")
    clearStorage()
    expect(readStorage("token")).toBeNull()
  })
})

describe("auth-cookie", () => {
  beforeEach(() => {
    document.cookie = ""
  })

  it("setAuthCookie и clearAuthCookie", () => {
    setAuthCookie()
    expect(document.cookie).toContain("dtp_auth=1")
    clearAuthCookie()
    expect(document.cookie).not.toContain("dtp_auth=1")
  })
})
