// тесты WS-хука: toast на newaccident
import { render, waitFor } from "@testing-library/react"
import { useEffect } from "react"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"

import AccidentNotifications from "@/hooks/accident-notifications"
import { AuthProvider } from "@/contexts/AuthContext"
import {
  NotificationsProvider,
  useNotificationsPanel,
} from "@/contexts/NotificationsContext"
import { jsonResponse, mockFetch, seedSession } from "../test-utils"

const toastMock = vi.fn()
vi.mock("@/hooks/use-toast", () => ({
  toast: (...args: unknown[]) => toastMock(...args),
}))

type WsListener = ((event: MessageEvent) => void) | null

class MockWebSocket {
  static instances: MockWebSocket[] = []
  url: string
  onopen: (() => void) | null = null
  onmessage: WsListener = null
  onerror: ((e: Event) => void) | null = null
  onclose: (() => void) | null = null

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
    queueMicrotask(() => this.onopen?.())
  }

  close() {
    this.onclose?.()
  }

  emit(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) } as MessageEvent)
  }
}

describe("AccidentNotifications", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    MockWebSocket.instances = []
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket)
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  function renderWs() {
    seedSession("ws-token", "admin")
    mockFetch({
      "/auth/verify": () => jsonResponse({ login: "admin" }),
      "/accidents": () =>
        jsonResponse({
          accidents: [{ id: 1, status: "new" }],
        }),
    })

    const refreshPanel = vi.fn()
    const refreshRef = { current: refreshPanel }

    const ui = (
      <AuthProvider>
        <NotificationsProvider>
          <AccidentNotifications />
          <NotificationsRegistrar onRefresh={refreshPanel} />
        </NotificationsProvider>
      </AuthProvider>
    )

    return { ...render(ui), refreshPanel }
  }

  it("подключается к WS с token", async () => {
    renderWs()
    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBeGreaterThan(0)
    })
    expect(MockWebSocket.instances[0].url).toContain("token=")
  })

  it("newaccident показывает toast и refreshPanel", async () => {
    const { refreshPanel } = renderWs()

    await waitFor(() => expect(MockWebSocket.instances.length).toBe(1))

    const ws = MockWebSocket.instances[0]
    ws.emit({
      event: "newaccident",
      data: { id: 99, created_at: "2024-06-15T12:00:00Z" },
    })

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalled()
      expect(refreshPanel).toHaveBeenCalled()
    })

    const toastArg = toastMock.mock.calls[0][0] as { className?: string }
    expect(toastArg.className).toBe("dtp-toast")
  })

  it("повторный newaccident для того же id не дублирует toast", async () => {
    renderWs()
    await waitFor(() => expect(MockWebSocket.instances.length).toBe(1))
    const ws = MockWebSocket.instances[0]

    ws.emit({ event: "newaccident", data: { id: 50, created_at: null } })
    await waitFor(() => expect(toastMock).toHaveBeenCalledTimes(1))

    ws.emit({ event: "newaccident", data: { id: 50, created_at: null } })
    await waitFor(() => expect(toastMock).toHaveBeenCalledTimes(1))
  })

  it("accidentupdated вызывает refreshPanel без toast", async () => {
    const { refreshPanel } = renderWs()
    await waitFor(() => expect(MockWebSocket.instances.length).toBe(1))

    toastMock.mockClear()
    MockWebSocket.instances[0].emit({
      event: "accidentupdated",
      data: { id: 1 },
    })

    await waitFor(() => expect(refreshPanel).toHaveBeenCalled())
    expect(toastMock).not.toHaveBeenCalled()
  })

  it("игнорирует ping", async () => {
    const { refreshPanel } = renderWs()
    await waitFor(() => expect(MockWebSocket.instances.length).toBe(1))

    refreshPanel.mockClear()
    MockWebSocket.instances[0].emit({ type: "ping" })

    await new Promise((r) => setTimeout(r, 50))
    expect(refreshPanel).not.toHaveBeenCalled()
    expect(toastMock).not.toHaveBeenCalled()
  })
})

function NotificationsRegistrar({ onRefresh }: { onRefresh: () => void }) {
  const { registerPanelRefresh } = useNotificationsPanel()
  useEffect(() => registerPanelRefresh(onRefresh), [onRefresh, registerPanelRefresh])
  return null
}
