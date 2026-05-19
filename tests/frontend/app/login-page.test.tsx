// тесты страницы входа
import { Suspense } from "react"
import { fireEvent, render, screen, waitFor, act } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"

import LoginPage from "@/app/login/page"
import { mockRouter } from "../test-utils-fetch"

const mockLogin = vi.fn()
const mockAuthState = {
  user: null as string | null,
  token: null as string | null,
  isLoading: false,
  isValid: false,
}

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    auth: mockAuthState,
    login: mockLogin,
    logout: vi.fn(),
  }),
}))

const mockSearchParams = new URLSearchParams()

vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
  usePathname: () => "/login",
  useSearchParams: () => mockSearchParams,
}))

function renderLoginPage() {
  return render(
    <Suspense fallback={<div data-testid="login-suspense">…</div>}>
      <LoginPage />
    </Suspense>,
  )
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSearchParams.delete("reset")
    Object.assign(mockAuthState, {
      user: null,
      token: null,
      isLoading: false,
      isValid: false,
    })
  })

  it("рендерит форму входа", () => {
    renderLoginPage()
    expect(screen.getByLabelText("Логин")).toBeInTheDocument()
    expect(screen.getByLabelText("Пароль")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Войти" })).toBeInTheDocument()
    expect(screen.getByText("Управление дорожным движением")).toBeInTheDocument()
  })

  it("показывает ошибку при неверных учётных данных", async () => {
    mockLogin.mockResolvedValue({ ok: false, reason: "invalid" })
    renderLoginPage()

    fireEvent.change(screen.getByLabelText("Логин"), { target: { value: "admin" } })
    fireEvent.change(screen.getByLabelText("Пароль"), { target: { value: "bad" } })

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Войти" }))
    })

    expect(await screen.findByRole("alert")).toHaveTextContent("Неверный логин или пароль")
    expect(mockRouter.replace).not.toHaveBeenCalledWith("/")
  })

  it("показывает ошибку сети", async () => {
    mockLogin.mockResolvedValue({ ok: false, reason: "network" })
    renderLoginPage()

    fireEvent.change(screen.getByLabelText("Логин"), { target: { value: "a" } })
    fireEvent.change(screen.getByLabelText("Пароль"), { target: { value: "b" } })

    await act(async () => {
      fireEvent.submit(screen.getByRole("button", { name: "Войти" }).closest("form")!)
    })

    expect(await screen.findByRole("alert")).toHaveTextContent("Сервер недоступен")
  })

  it("успешный вход перенаправляет на главную", async () => {
    mockLogin.mockResolvedValue({ ok: true })
    renderLoginPage()

    fireEvent.change(screen.getByLabelText("Логин"), { target: { value: "admin" } })
    fireEvent.change(screen.getByLabelText("Пароль"), { target: { value: "admin123" } })

    await act(async () => {
      fireEvent.submit(screen.getByRole("button", { name: "Войти" }).closest("form")!)
    })

    await waitFor(() => {
      expect(mockRouter.replace).toHaveBeenCalledWith("/")
    })
  })

  it("показывает спиннер при isLoading", () => {
    mockAuthState.isLoading = true
    renderLoginPage()
    expect(screen.getByText("Загрузка…")).toBeInTheDocument()
  })

  it("редиректит авторизованного пользователя", async () => {
    mockAuthState.isValid = true
    mockAuthState.user = "admin"
    renderLoginPage()

    await waitFor(() => {
      expect(mockRouter.replace).toHaveBeenCalledWith("/")
    })
  })

  it("?reset=1 очищает форму", async () => {
    mockSearchParams.set("reset", "1")
    renderLoginPage()

    await waitFor(() => {
      expect(mockRouter.replace).toHaveBeenCalledWith("/login")
    })
    expect(screen.getByLabelText("Логин")).toHaveValue("")
    expect(screen.getByLabelText("Пароль")).toHaveValue("")
  })
})
