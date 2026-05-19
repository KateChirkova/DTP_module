"use client"

// боковая панель уведомлений (live API или demo)
import { Drawer, DrawerContent, DrawerTrigger } from "@/components/ui/drawer"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Notification } from "@/hooks/use-notifications"
import { formatDateMoscow, formatTimeMoscow } from "@/lib/datetime"
import { dismissAllToasts } from "@/lib/ui-events"

type NotificationDrawerLiveProps = {
  demo?: false
  children: React.ReactNode
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  markRead: (id: number) => Promise<void>
  markAllRead: () => Promise<void>
  refresh?: () => Promise<void>
}

type NotificationDrawerDemoProps = {
  demo: true
  children: React.ReactNode
  demoUnreadCount?: number
  demoEmptyMessage?: string
}

export type NotificationDrawerProps = NotificationDrawerLiveProps | NotificationDrawerDemoProps

function DrawerPanel({
  unreadCount,
  isLoading,
  notifications,
  markRead,
  onMarkAllRead,
  demo,
  demoEmptyMessage,
}: {
  unreadCount: number
  isLoading: boolean
  notifications: Notification[]
  markRead?: (id: number) => Promise<void>
  onMarkAllRead?: () => void
  demo?: boolean
  demoEmptyMessage?: string
}) {
  return (
    <DrawerContent className="dtp-drawer">
      <div className="dtp-drawer__wrap">
        <div className="dtp-drawer__header">
          <p className="dtp-drawer__title">Уведомления</p>
          <div className="dtp-drawer__actions">
            <Badge className="dtp-drawer__badge">{unreadCount}</Badge>
            <Button
              variant="ghost"
              size="sm"
              className="dtp-drawer__markall"
              onClick={onMarkAllRead}
              disabled={unreadCount === 0 || demo}
            >
              Прочитать все
            </Button>
          </div>
        </div>
        <div className="dtp-drawer__list">
          {demo ? (
            <div className="dtp-drawer__empty">{demoEmptyMessage}</div>
          ) : isLoading ? (
            <div className="dtp-drawer__empty">Загрузка…</div>
          ) : notifications.length === 0 ? (
            <div className="dtp-drawer__empty">Пока пусто</div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`dtp-drawer__item ${
                  notification.status === "unread" ? "dtp-drawer__item--unread" : ""
                }`}
                onClick={() =>
                  notification.status === "unread" && markRead?.(notification.id)
                }
              >
                <div className="dtp-drawer__itemContent">
                  <span className="dtp-drawer__itemTitle">
                    ДТП: {formatTimeMoscow(notification.created_at)}
                  </span>
                  <div className="dtp-drawer__itemMeta">
                    {formatDateMoscow(notification.created_at)}
                  </div>
                </div>
                {notification.status === "unread" && (
                  <Badge className="dtp-drawer__new">Новое</Badge>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </DrawerContent>
  )
}

export function NotificationDrawer(props: NotificationDrawerProps) {
  if (props.demo) {
    const unreadCount = props.demoUnreadCount ?? 2
    return (
      <Drawer direction="right">
        <DrawerTrigger asChild>{props.children}</DrawerTrigger>
        <DrawerPanel
          unreadCount={unreadCount}
          isLoading={false}
          notifications={[]}
          demo
          demoEmptyMessage={
            props.demoEmptyMessage ??
            "Демо: здесь будет список уведомлений из вашего API"
          }
        />
      </Drawer>
    )
  }

  // при открытии — убрать toast и подтянуть список
  const handleOpenChange = (open: boolean) => {
    dismissAllToasts()
    if (open && props.refresh) void props.refresh()
  }

  const handleMarkAllRead = () => {
    dismissAllToasts()
    void props.markAllRead()
  }

  return (
    <Drawer direction="right" onOpenChange={handleOpenChange}>
      <DrawerTrigger asChild>{props.children}</DrawerTrigger>
      <DrawerPanel
        unreadCount={props.unreadCount}
        isLoading={props.isLoading}
        notifications={props.notifications}
        markRead={props.markRead}
        onMarkAllRead={handleMarkAllRead}
      />
    </Drawer>
  )
}
