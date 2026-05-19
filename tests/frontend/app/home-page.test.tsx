// тесты главной страницы
import type { ReactNode } from "react"
import { fireEvent, screen, waitFor } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"

import HomePage from "@/app/page"
import { jsonResponse, mockFetch, seedSession } from "../test-utils-fetch"
import { renderWithProviders } from "../test-utils"

vi.mock("@/components/traffic-shell/map-wrapper", () => ({
  default: ({ overlay }: { overlay?: ReactNode }) => (
    <div data-testid="map-stub">{overlay}</div>
  ),
}))

describe("HomePage", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it("без сессии не показывает контент карты", async () => {
    mockFetch({})
    renderWithProviders(<HomePage />)

    await waitFor(() => {
      expect(screen.queryByLabelText("Уведомления о ДТП")).not.toBeInTheDocument()
    })
    expect(screen.getByText(/Перенаправление на вход|Проверка сессии/)).toBeInTheDocument()
  })

  it("с сессией показывает shell и FAB", async () => {
    seedSession("tok", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ success: true, login: "admin" }),
      "/notifications": () =>
        jsonResponse({
          success: true,
          total: 0,
          unread_count: 0,
          limit: 20,
          offset: 0,
          data: [],
        }),
    })

    renderWithProviders(<HomePage />)

    expect(await screen.findByText("Управление дорожным движением")).toBeInTheDocument()
    expect(await screen.findByLabelText("Уведомления о ДТП")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Выйти из сервиса" })).toBeInTheDocument()
    expect(screen.getByTestId("map-stub")).toBeInTheDocument()
  })

  it("открывает drawer уведомлений", async () => {
    seedSession("tok", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ login: "admin" }),
      "/notifications": () =>
        jsonResponse({
          success: true,
          total: 1,
          unread_count: 1,
          limit: 20,
          offset: 0,
          data: [
            {
              id: 1,
              accident_id: 42,
              status: "unread",
              created_at: "2024-06-15T10:00:00Z",
            },
          ],
        }),
    })

    renderWithProviders(<HomePage />)

    const fab = await screen.findByLabelText("Уведомления о ДТП")
    fireEvent.click(fab)

    expect(await screen.findByText("Уведомления")).toBeInTheDocument()
    expect(screen.getByText(/ДТП:/)).toBeInTheDocument()
  })
})
