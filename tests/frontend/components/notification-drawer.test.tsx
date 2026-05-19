// тесты NotificationDrawer (live и demo)
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { NotificationDrawer } from "@/components/notification-drawer"
import { dismissAllToasts, registerToastDismiss } from "@/lib/ui-events"

const notifications = [
  {
    id: 1,
    accident_id: 5,
    status: "unread" as const,
    created_at: "2024-06-15T10:00:00Z",
  },
]

describe("NotificationDrawer", () => {
  it("demo режим показывает заглушку", async () => {
    render(
      <NotificationDrawer demo demoUnreadCount={3}>
        <button type="button">open</button>
      </NotificationDrawer>,
    )

    fireEvent.click(screen.getByRole("button", { name: "open" }))

    expect(await screen.findByText("Уведомления")).toBeInTheDocument()
    expect(screen.getByText(/Демо:/)).toBeInTheDocument()
    expect(screen.getByText("3")).toBeInTheDocument()
  })

  it("live режим показывает список и вызывает markRead", async () => {
    const markRead = vi.fn()
    const markAllRead = vi.fn()

    render(
      <NotificationDrawer
        notifications={notifications}
        unreadCount={1}
        isLoading={false}
        markRead={markRead}
        markAllRead={markAllRead}
      >
        <button type="button">open-live</button>
      </NotificationDrawer>,
    )

    fireEvent.click(screen.getByRole("button", { name: "open-live" }))

    expect(await screen.findByText(/ДТП:/)).toBeInTheDocument()
    expect(screen.getByText("Новое")).toBeInTheDocument()

    fireEvent.click(screen.getByText(/ДТП:/))
    expect(markRead).toHaveBeenCalledWith(1)
  })

  it("при открытии вызывает dismissAllToasts и refresh", async () => {
    const dismiss = vi.fn()
    const refresh = vi.fn().mockResolvedValue(undefined)
    registerToastDismiss(dismiss)

    render(
      <NotificationDrawer
        notifications={[]}
        unreadCount={0}
        isLoading={false}
        markRead={vi.fn()}
        markAllRead={vi.fn()}
        refresh={refresh}
      >
        <button type="button">open-refresh</button>
      </NotificationDrawer>,
    )

    fireEvent.click(screen.getByRole("button", { name: "open-refresh" }))

    await waitFor(() => {
      expect(dismiss).toHaveBeenCalled()
      expect(refresh).toHaveBeenCalled()
    })
  })
})
