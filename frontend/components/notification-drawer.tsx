"use client"

import { useEffect } from "react"
import { Drawer, DrawerContent, DrawerTrigger } from "@/components/ui/drawer"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useNotifications } from "@/hooks/use-notifications"

interface NotificationDrawerProps {
  children: React.ReactNode
  refresh?: () => void
}

const API_BASE = "http://127.0.0.1:8080"

export function NotificationDrawer({ children }: NotificationDrawerProps) {
  const { notifications, unreadCount, isLoading, refresh } = useNotifications()

  const markRead = async (id: number) => {
    await fetch(`${API_BASE}/api/v1/notifications/${id}/read`, { method: "PUT" })
    refresh()
  }

  const markAllRead = async () => {
    await Promise.all(
      notifications
        .filter((n) => n.status === "unread")
        .map((n) => fetch(`${API_BASE}/api/v1/notifications/${n.id}/read`, { method: "PUT" }))
    )
    refresh()
  }

  useEffect(() => {
    const interval = setInterval(refresh, 5000)
    return () => clearInterval(interval)
  }, [refresh])

  return (
    <Drawer direction="right">
      <DrawerTrigger asChild>{children}</DrawerTrigger>
      <DrawerContent className="dtp-drawer">
        <div className="dtp-drawer__wrap">
          <div className="dtp-drawer__header">
            <h3 className="dtp-drawer__title">ДТП</h3>
            <div className="dtp-drawer__actions">
              <Badge className="dtp-drawer__badge">{unreadCount}</Badge>
              <Button
                variant="ghost"
                size="sm"
                className="dtp-drawer__markall"
                onClick={markAllRead}
                disabled={!notifications.length || unreadCount === 0}
              >
                Прочитать
              </Button>
            </div>
          </div>
          <div className="dtp-drawer__list">
            {isLoading ? (
              <div className="dtp-drawer__empty">Загрузка…</div>
            ) : notifications.length === 0 ? (
              <div className="dtp-drawer__empty">Пока пусто</div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={
                    notification.status === "unread"
                      ? "dtp-drawer__item dtp-drawer__item--unread"
                      : "dtp-drawer__item"
                  }
                  onClick={() => notification.status === "unread" && markRead(notification.id)}
                >
                  <div className="dtp-drawer__itemTop">
                    <span className="dtp-drawer__itemTitle">ДТП #{notification.accident_id}</span>
                    {notification.status === "unread" && (
                      <Badge className="dtp-drawer__new">Новое</Badge>
                    )}
                  </div>
                  <div className="dtp-drawer__itemMeta">
                    {notification.created_at
                      ? new Date(notification.created_at).toLocaleString("ru-RU")
                      : ""}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  )
}