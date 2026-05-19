"use client"

import { useCallback, useEffect, useState } from "react"

import { useAuth } from "@/contexts/AuthContext"
import { useNotificationsPanel } from "@/contexts/NotificationsContext"
import { logAppError } from "@/lib/app-log"
import { devLog } from "@/lib/dev-log"
import { apiFetch } from "@/lib/http"

// резервный опрос, если WS недоступен
const NOTIFICATIONS_POLL_MS = 30_000

export type Notification = {
  id: number
  accident_id: number
  status: "unread" | "read"
  accident_status?: string | null
  created_at: string | null
}

type NotificationsResponse = {
  success: boolean
  total: number
  unread_count: number
  limit: number
  offset: number
  data: Notification[]
}

export function useNotifications() {
  const [data, setData] = useState<NotificationsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const { auth } = useAuth()
  const { registerPanelRefresh } = useNotificationsPanel()

  const load = useCallback(
    async (status: "unread" | "read" | "all" = "all", opts?: { silent?: boolean }) => {
      const silent = opts?.silent ?? false

      if (!auth.isValid || !auth.token) {
        devLog("Notifications: ожидание авторизации...")
        setData(null)
        setIsLoading(false)
        return
      }

      try {
        if (!silent) setIsLoading(true)
        setError(null)

        const result = await apiFetch<NotificationsResponse>(
          `/api/v1/notifications?status=${status}`,
          { token: auth.token },
        )

        if (!result.ok) {
          if (result.status === 401) {
            setData(null)
            return
          }
          throw new Error(`HTTP ${result.status}`)
        }

        setData(result.data)
      } catch (e) {
        logAppError("notifications.load", e)
        setError(e)
        setData(null)
      } finally {
        if (!silent) setIsLoading(false)
      }
    },
    [auth.isValid, auth.token],
  )

  const markRead = useCallback(
    async (id: number) => {
      if (!auth.token || !auth.isValid) return

      const result = await apiFetch(`/api/v1/notifications/${id}/read`, {
        token: auth.token,
        method: "PUT",
      })

      if (!result.ok) {
        if (result.status !== 401) {
          logAppError("notifications.markRead", { notificationId: id, status: result.status })
          await load("all")
        }
        return
      }

      setData((prev) => {
        if (!prev) return prev
        const nextItems = prev.data.map((n) =>
          n.id === id ? { ...n, status: "read" as const } : n,
        )
        return {
          ...prev,
          data: nextItems,
          unread_count: nextItems.filter((n) => n.status === "unread").length,
        }
      })
    },
    [auth.isValid, auth.token, load],
  )

  const markAllRead = useCallback(async () => {
    if (!auth.token || !auth.isValid || !data) return

    const result = await apiFetch("/api/v1/notifications/read-all", {
      token: auth.token,
      method: "PUT",
    })

    if (!result.ok) {
      if (result.status !== 401) {
        logAppError("notifications.markAllRead", { status: result.status })
        await load("all")
      }
      return
    }

    setData((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        unread_count: 0,
        data: prev.data.map((n) => ({ ...n, status: "read" as const })),
      }
    })
  }, [auth.token, auth.isValid, data, load])

  useEffect(() => {
    if (!auth.isValid) {
      setData(null)
      setIsLoading(false)
      return
    }

    void load("all")
    const interval = setInterval(() => void load("all", { silent: true }), NOTIFICATIONS_POLL_MS)
    return () => clearInterval(interval)
  }, [load, auth.isValid])

  useEffect(() => {
    return registerPanelRefresh(() => {
      void load("all", { silent: true })
    })
  }, [load, registerPanelRefresh])

  const refresh = useCallback(() => load("all", { silent: false }), [load])

  return {
    notifications: data?.data ?? [],
    unreadCount: data?.unread_count ?? 0,
    total: data?.total ?? 0,
    isLoading,
    isError: Boolean(error),
    error,
    refresh,
    markRead,
    markAllRead,
  }
}
