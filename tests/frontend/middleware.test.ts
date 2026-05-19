// тесты middleware: redirect без dtp_auth
import { NextRequest } from "next/server"
import { describe, expect, it } from "vitest"

import { middleware } from "@/middleware"

function makeRequest(pathname: string, cookie?: string) {
  const url = new URL(`http://localhost:3000${pathname}`)
  const headers = cookie ? { cookie: `dtp_auth=${cookie}` } : undefined
  return new NextRequest(url, { headers })
}

describe("middleware", () => {
  it("пропускает /login без cookie", () => {
    const res = middleware(makeRequest("/login"))
    expect(res.status).toBe(200)
    expect(res.headers.get("location")).toBeNull()
  })

  it("пропускает статику _next", () => {
    const res = middleware(makeRequest("/_next/static/chunk.js"))
    expect(res.status).toBe(200)
  })

  it("пропускает файлы с точкой в пути", () => {
    const res = middleware(makeRequest("/favicon.ico"))
    expect(res.status).toBe(200)
  })

  it("редиректит на /login без dtp_auth", () => {
    const res = middleware(makeRequest("/dtp"))
    expect(res.status).toBe(307)
    expect(res.headers.get("location")).toMatch(/\/login$/)
  })

  it("пропускает защищённый маршрут с dtp_auth=1", () => {
    const res = middleware(makeRequest("/dtp", "1"))
    expect(res.status).toBe(200)
    expect(res.headers.get("location")).toBeNull()
  })
})
