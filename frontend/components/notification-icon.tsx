"use client"

import { AlertTriangle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { NotificationDrawer } from "@/components/notification-drawer"
import { useNotifications } from "@/hooks/use-notifications"

export function NotificationIcon() {
  const { unreadCount, refresh } = useNotifications()

  return (
    <div className="dtp-fab">
      <NotificationDrawer refresh={refresh}>
        <button
          aria-label="Уведомления о ДТП"
          className="dtp-fab__button"
        >
          <AlertTriangle
            className="dtp-fab__icon"
          />

          {unreadCount > 0 && (
            <Badge className="dtp-fab__badge">
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
        </button>
      </NotificationDrawer>
    </div>
  )
}