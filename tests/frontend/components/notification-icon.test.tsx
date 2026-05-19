// тесты FAB NotificationIcon
import { render, screen, waitFor } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"

import { NotificationIcon } from "@/components/notification-icon"
import { NotificationsProvider } from "@/contexts/NotificationsContext"
import { jsonResponse, mockFetch } from "../test-utils"

const mockAuth = vi.fn(() => ({
  auth: { user: "u", token: "tok", isLoading: false, isValid: true },
  login: vi.fn(),
  logout: vi.fn(),
}))

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockAuth(),
}))

describe("NotificationIcon", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("показывает badge с числом непрочитанных", async () => {
    mockFetch({
      "/notifications": () =>
        jsonResponse({
          success: true,
          total: 1,
          unread_count: 2,
          limit: 20,
          offset: 0,
          data: [
            {
              id: 1,
              accident_id: 1,
              status: "unread",
              created_at: "2024-06-15T10:00:00Z",
            },
          ],
        }),
    })

    render(
      <NotificationsProvider>
        <NotificationIcon />
      </NotificationsProvider>,
    )

    expect(await screen.findByLabelText("Уведомления о ДТП")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText("2")).toBeInTheDocument()
    })
  })

  it("показывает 9+ при unread > 9", async () => {
    mockFetch({
      "/notifications": () =>
        jsonResponse({
          success: true,
          total: 10,
          unread_count: 12,
          limit: 20,
          offset: 0,
          data: [],
        }),
    })

    render(
      <NotificationsProvider>
        <NotificationIcon />
      </NotificationsProvider>,
    )

    expect(await screen.findByText("9+")).toBeInTheDocument()
  })
})
