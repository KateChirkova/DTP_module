"use client"
import { useEffect, useRef } from "react"
import { useToast } from "@/hooks/use-toast"
import { useNotifications } from "@/hooks/use-notifications"

export default function AccidentNotifications() {
  const { toast } = useToast()
  const { refresh } = useNotifications()
  const wsRef = useRef<WebSocket | null>(null)
  useEffect(() => {
    const token = localStorage.getItem("token") || "guest"
    const wsUrl = `ws://127.0.0.1:8080/api/v1/ws/notifications?token=${token}`

    if (wsRef.current) {
      wsRef.current.close()
    }

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => console.log("🔌 WS OK:", wsUrl)

    ws.onmessage = (event) => {
      try {
        const { event: type, data } = JSON.parse(event.data)
        console.log("📱 WS:", type, data)

        if (type === "newaccident") {
          toast({ title: "Новое ДТП!", description: `ID ${data.id}` })
        } else if (type === "accidentupdated") {
          toast({ title: "Обновлено", description: `ID ${data.id}` })
        } else if (type === "accidentresolved") {
          toast({ title: "Разрешено", description: `ID ${data.id}` })
        }
        refresh()
      } catch (e) {
        console.error("Parse error:", e)
      }
    }

    ws.onerror = (error) => console.error("WS error:", error)
    ws.onclose = () => {
      console.log("WS closed")
      wsRef.current = null
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  return null
}