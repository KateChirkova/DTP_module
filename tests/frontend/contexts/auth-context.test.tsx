// тесты AuthContext: login, verify, RequireAuth
import { fireEvent, render, screen, waitFor, act } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"

import { jsonResponse, mockFetch, mockRouter, seedSession } from "../test-utils-fetch"
import { AuthProvider, RequireAuth, useAuth } from "@/contexts/AuthContext"

function AuthProbe() {
  const { auth, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <span data-testid="valid">{String(auth.isValid)}</span>
      <span data-testid="user">{auth.user ?? ""}</span>
      <button type="button" onClick={() => void login("u", "p")}>
        login
      </button>
      <button type="button" onClick={() => logout()}>
        logout
      </button>
    </div>
  )
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear()
    document.cookie = ""
    vi.clearAllMocks()
  })

  it("init без token — не авторизован", async () => {
    mockFetch({})
    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    )
    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false")
    })
    expect(screen.getByTestId("valid")).toHaveTextContent("false")
  })

  it("init с валидным token — verify и авторизация", async () => {
    seedSession("good-token", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ success: true, login: "admin" }),
    })
    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    )
    await waitFor(() => {
      expect(screen.getByTestId("valid")).toHaveTextContent("true")
    })
    expect(screen.getByTestId("user")).toHaveTextContent("admin")
  })

  it("login успешен сохраняет token и user", async () => {
    mockFetch({
      "/auth/login": () =>
        jsonResponse({ success: true, token: "new-tok", user: "ivan" }),
    })
    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("false"))

    await act(async () => {
      fireEvent.click(screen.getByText("login"))
    })

    await waitFor(() => {
      expect(screen.getByTestId("valid")).toHaveTextContent("true")
      expect(screen.getByTestId("user")).toHaveTextContent("ivan")
    })
    expect(localStorage.getItem("token")).toBe("new-tok")
  })

  it("login 401 — остаётся неавторизованным", async () => {
    mockFetch({
      "/auth/login": () => jsonResponse({}, 401),
    })
    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("false"))

    await act(async () => {
      fireEvent.click(screen.getByText("login"))
    })

    expect(screen.getByTestId("valid")).toHaveTextContent("false")
  })

  it("logout очищает сессию и редиректит", async () => {
    seedSession("t", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ login: "admin" }),
      "/auth/logout": () => jsonResponse({ success: true }),
    })
    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId("valid")).toHaveTextContent("true"))

    act(() => {
      fireEvent.click(screen.getByText("logout"))
    })

    expect(screen.getByTestId("valid")).toHaveTextContent("false")
    expect(localStorage.getItem("token")).toBeNull()
    expect(mockRouter.replace).toHaveBeenCalledWith("/login?reset=1")
  })
})

describe("RequireAuth", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it("показывает children когда авторизован", async () => {
    seedSession("t", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ login: "admin" }),
    })
    render(
      <AuthProvider>
        <RequireAuth>
          <div>protected</div>
        </RequireAuth>
      </AuthProvider>,
    )
    await waitFor(() => {
      expect(screen.getByText("protected")).toBeInTheDocument()
    })
  })

  it("редирект на login без сессии", async () => {
    mockFetch({})
    render(
      <AuthProvider>
        <RequireAuth>
          <div>protected</div>
        </RequireAuth>
      </AuthProvider>,
    )
    await waitFor(() => {
      expect(mockRouter.replace).toHaveBeenCalledWith("/login")
    })
    expect(screen.queryByText("protected")).not.toBeInTheDocument()
  })
})
