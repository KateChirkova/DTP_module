"use client"

import { AlertTriangle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { NotificationDrawer } from "@/components/notification-drawer"

// демо-слой ДТП для встраивания в traffic_krasnodar (без API)
export function DtpMapOverlayDemo() {
  return (
    <div className="dtp-fab">
      <NotificationDrawer demo demoUnreadCount={2}>
        <button type="button" aria-label="Уведомления о ДТП (демо)" className="dtp-fab__button">
          <AlertTriangle className="dtp-fab__icon" aria-hidden />
          <Badge className="dtp-fab__badge">2</Badge>
        </button>
      </NotificationDrawer>
    </div>
  )
}
