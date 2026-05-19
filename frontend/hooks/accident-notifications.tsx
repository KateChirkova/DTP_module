"use client"

// WebSocket: toast на новое ДТП, обновление панели уведомлений
import { useEffect, useRef } from "react"
import { AlertTriangle } from "lucide-react"

import { useAuth } from "@/contexts/AuthContext"
import { useNotificationsPanel } from "@/contexts/NotificationsContext"
import { toast } from "@/hooks/use-toast"
import { formatTimeMoscow } from "@/lib/datetime"
import { logAppError, logAppWarn } from "@/lib/app-log"
import { apiFetch, wsNotificationsUrl } from "@/lib/http"

const WS_RECONNECT_MS = 1500

export default function AccidentNotifications() {
  const { auth } = useAuth()
  const { refreshPanel } = useNotificationsPanel()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const shouldReconnectRef = useRef(true)
  const seenAccidentsRef = useRef<Set<number>>(new Set())

  useEffect(() => {
    if (!auth.isValid || !auth.token) {
      shouldReconnectRef.current = false
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
      wsRef.current = null
      seenAccidentsRef.current = new Set()
      return
    }

    shouldReconnectRef.current = true
    const token = auth.token

    const showToast = (createdAt?: string | null) => {
      toast({
        className: "dtp-toast",
        duration: 30000,
        title: (
          <div className="dtp-toast__content">
            <AlertTriangle className="dtp-toast__icon" />
            <div className="dtp-toast__body">
              <div className="dtp-toast__headline">Новое ДТП!</div>
              <div className="dtp-toast__subline">
                Время:{" "}
                {formatTimeMoscow(
                  createdAt,
                  new Date().toLocaleTimeString("ru-RU", {
                    hour: "2-digit",
                    minute: "2-digit",
                    timeZone: "Europe/Moscow",
                  }),
                )}
              </div>
            </div>
          </div>
        ),
      })
    }

    const seedSeenAccidents = async () => {
      const result = await apiFetch<{
        accidents?: Array<{ id: number; status?: string }>
      }>("/api/v1/accidents?status=new&limit=100", { token })
      if (!result.ok) {
        logAppWarn("accidents.seedSeen", { status: result.status })
        return
      }
      const ids = (result.data.accidents ?? [])
        .filter((a) => a.status === "new")
        .map((a) => a.id)
      seenAccidentsRef.current = new Set(ids)
    }

    const handleWsMessage = (event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data) as {
          type?: string
          event?: string
          data?: { id?: number; created_at?: string | null; status?: string }
        }
        if (parsed.type === "ping") return

        const type = parsed.event
        const data = parsed.data
        if (!type) return
        if (!data) {
          if (type !== "notifications_updated") {
            logAppWarn("ws.accident.missingData", { event: type })
          }
          return
        }

        if (type === "newaccident" && data.id != null) {
          refreshPanel()
          if (!seenAccidentsRef.current.has(data.id)) {
            seenAccidentsRef.current.add(data.id)
            showToast(data.created_at)
          }
          return
        }

        if (
          type === "accidentupdated" ||
          type === "accidentresolved" ||
          type === "notifications_updated"
        ) {
          refreshPanel()
        }
      } catch (e) {
        logAppError("ws.parse", e)
      }
    }

    const connect = () => {
      wsRef.current?.close()
      const ws = new WebSocket(wsNotificationsUrl(token))
      wsRef.current = ws

      ws.onopen = () => {
        void seedSeenAccidents()
      }
      ws.onmessage = handleWsMessage
      ws.onerror = (error) => logAppError("ws.connection", error)
      ws.onclose = () => {
        wsRef.current = null
        if (!shouldReconnectRef.current) return
        reconnectTimerRef.current = setTimeout(connect, WS_RECONNECT_MS)
      }
    }

    connect()

    return () => {
      shouldReconnectRef.current = false
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [auth.isValid, auth.token, refreshPanel])

  return null
}
