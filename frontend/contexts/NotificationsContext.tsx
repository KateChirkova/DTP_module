"use client"

// связь WS-событий с перезагрузкой списка уведомлений
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  type ReactNode,
} from "react"

type NotificationsContextValue = {
  refreshPanel: () => void
  registerPanelRefresh: (fn: () => void) => () => void
}

const NotificationsContext = createContext<NotificationsContextValue | null>(null)

export function NotificationsProvider({ children }: { children: ReactNode }) {
  const refreshRef = useRef<(() => void) | null>(null)

  const registerPanelRefresh = useCallback((fn: () => void) => {
    refreshRef.current = fn
    return () => {
      if (refreshRef.current === fn) {
        refreshRef.current = null
      }
    }
  }, [])

  const refreshPanel = useCallback(() => {
    refreshRef.current?.()
  }, [])

  const value = useMemo(
    () => ({ refreshPanel, registerPanelRefresh }),
    [refreshPanel, registerPanelRefresh],
  )

  return (
    <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>
  )
}

export function useNotificationsPanel() {
  const ctx = useContext(NotificationsContext)
  if (!ctx) {
    throw new Error("useNotificationsPanel must be used within NotificationsProvider")
  }
  return ctx
}
