"use client"

// FAB на карте: счётчик непрочитанных + drawer
import { AlertTriangle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { NotificationDrawer } from "@/components/notification-drawer"
import { useNotifications } from "@/hooks/use-notifications"

export function NotificationIcon() {
  const { notifications, unreadCount, isLoading, markRead, markAllRead, refresh } = useNotifications()

  return (
    <div className="dtp-fab">
      <NotificationDrawer
        notifications={notifications}
        unreadCount={unreadCount}
        isLoading={isLoading}
        markRead={markRead}
        markAllRead={markAllRead}
        refresh={refresh}
      >
        <button
          aria-label="Уведомления о ДТП"
          className="dtp-fab__button"
        >
          <AlertTriangle width={28} height={28} className="dtp-fab__icon" aria-hidden />

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