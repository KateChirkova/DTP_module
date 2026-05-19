// тесты NotificationsContext: refreshPanel
import { renderHook, act } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import {
  NotificationsProvider,
  useNotificationsPanel,
} from "@/contexts/NotificationsContext"

describe("NotificationsContext", () => {
  it("refreshPanel вызывает зарегистрированный callback", () => {
    const refresh = vi.fn()
    const { result } = renderHook(
      () => {
        const panel = useNotificationsPanel()
        return panel
      },
      { wrapper: NotificationsProvider },
    )

    act(() => {
      result.current.registerPanelRefresh(refresh)
    })

    act(() => {
      result.current.refreshPanel()
    })

    expect(refresh).toHaveBeenCalledOnce()
  })

  it("unregister снимает callback", () => {
    const refresh = vi.fn()
    const { result } = renderHook(() => useNotificationsPanel(), {
      wrapper: NotificationsProvider,
    })

    act(() => {
      const unregister = result.current.registerPanelRefresh(refresh)
      unregister()
      result.current.refreshPanel()
    })

    expect(refresh).not.toHaveBeenCalled()
  })
})
