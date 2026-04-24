"use client"

import { useEffect, useState, useCallback } from "react"

export type Notification = {
  id: number
  accident_id: number
  status: "unread" | "read"
  created_at: string | null
  is_sent: boolean
}

type NotificationsResponse = {
  success: boolean
  total: number
  unread_count: number
  limit: number
  offset: number
  data: Notification[]
}

const API_BASE = "http://127.0.0.1:8080"

export function useNotifications() {
  const [data, setData] = useState<NotificationsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  const load = useCallback(async (status: "unread" | "read" | "all" = "all") => {
    try {
      setIsLoading(true)
      const res = await fetch(`${API_BASE}/api/v1/notifications?status=${status}`, {
        cache: "no-store",
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = (await res.json()) as NotificationsResponse
      setData(json)
      setError(null)
    } catch (e) {
      setError(e)
      setData(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    load("all")
  }, [load])

  return {
    notifications: data?.data ?? [],
    unreadCount: data?.unread_count ?? 0,
    total: data?.total ?? 0,
    isLoading,
    isError: !!error,
    refresh: () => load("all"),
  }
}