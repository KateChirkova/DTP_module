// тесты useNotifications: загрузка, markRead
import { render, renderHook, waitFor, act } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"
import { useEffect } from "react"

import { useNotifications } from "@/hooks/use-notifications"
import { NotificationsProvider, useNotificationsPanel } from "@/contexts/NotificationsContext"
import { jsonResponse, mockFetch } from "../test-utils"

const sampleList = {
  success: true,
  total: 2,
  unread_count: 1,
  limit: 20,
  offset: 0,
  data: [
    {
      id: 1,
      accident_id: 10,
      status: "unread" as const,
      created_at: "2024-06-15T10:00:00Z",
    },
    {
      id: 2,
      accident_id: 11,
      status: "read" as const,
      created_at: "2024-06-15T11:00:00Z",
    },
  ],
}

const mockAuth = vi.fn(() => ({
  auth: {
    user: "user1",
    token: "tok",
    isLoading: false,
    isValid: true,
  },
  login: vi.fn(),
  logout: vi.fn(),
}))

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => mockAuth(),
}))

function NotificationsWrapper({ children }: { children: React.ReactNode }) {
  return <NotificationsProvider>{children}</NotificationsProvider>
}

describe("useNotifications", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuth.mockReturnValue({
      auth: { user: "user1", token: "tok", isLoading: false, isValid: true },
      login: vi.fn(),
      logout: vi.fn(),
    })
  })

  it("загружает список уведомлений", async () => {
    mockFetch({
      "/notifications": () => jsonResponse(sampleList),
    })

    const { result } = renderHook(() => useNotifications(), {
      wrapper: NotificationsWrapper,
    })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.notifications).toHaveLength(2)
    expect(result.current.unreadCount).toBe(1)
  })

  it("markRead помечает уведомление прочитанным локально", async () => {
    mockFetch({
      "/notifications": () => jsonResponse(sampleList),
      "/notifications/1/read": () => jsonResponse({ success: true, status: "read" }),
    })

    const { result } = renderHook(() => useNotifications(), {
      wrapper: NotificationsWrapper,
    })

    await waitFor(() => expect(result.current.notifications.length).toBe(2))

    await act(async () => {
      await result.current.markRead(1)
    })

    expect(result.current.unreadCount).toBe(0)
    expect(result.current.notifications.find((n) => n.id === 1)?.status).toBe("read")
  })

  it("markAllRead обнуляет unread_count", async () => {
    mockFetch({
      "/notifications": () => jsonResponse(sampleList),
      "/notifications/read-all": () => jsonResponse({ success: true }),
    })

    const { result } = renderHook(() => useNotifications(), {
      wrapper: NotificationsWrapper,
    })

    await waitFor(() => expect(result.current.unreadCount).toBe(1))

    await act(async () => {
      await result.current.markAllRead()
    })

    expect(result.current.unreadCount).toBe(0)
    expect(result.current.notifications.every((n) => n.status === "read")).toBe(true)
  })

  it("refreshPanel из NotificationsContext перезагружает список", async () => {
    let calls = 0
    mockFetch({
      "/notifications": () => {
        calls += 1
        return jsonResponse(sampleList)
      },
    })

    function Harness() {
      const { unreadCount } = useNotifications()
      const { refreshPanel } = useNotificationsPanel()
      useEffect(() => {
        refreshPanel()
      }, [refreshPanel])
      return <span data-testid="count">{unreadCount}</span>
    }

    render(
      <NotificationsProvider>
        <Harness />
      </NotificationsProvider>,
    )

    await waitFor(() => expect(calls).toBeGreaterThanOrEqual(2))
  })

  it("без авторизации не вызывает API", async () => {
    mockAuth.mockReturnValue({
      auth: { user: null, token: null, isLoading: false, isValid: false },
      login: vi.fn(),
      logout: vi.fn(),
    })

    const fetchMock = mockFetch({
      "/notifications": () => jsonResponse(sampleList),
    })

    const { result } = renderHook(() => useNotifications(), {
      wrapper: NotificationsWrapper,
    })

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.notifications).toEqual([])
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
