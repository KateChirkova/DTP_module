"use client"

// главная: карта, FAB уведомлений, выход
import { LogOut } from "lucide-react"

import { NotificationIcon } from "@/components/notification-icon"
import { TrafficPageShell } from "@/components/traffic-shell"
import { RequireAuth, useAuth } from "@/contexts/AuthContext"
import { EmbedUiIconButton } from "@/modules/embed-ui"
import shellStyles from "@/components/traffic-shell/traffic-shell.module.css"

const ICON_PROPS = { width: 16, height: 16, color: "#171717" as const }

function HomeContent() {
  const { logout } = useAuth()

  const headerTrailing = (
    <EmbedUiIconButton
      type="button"
      aria-label="Выйти из сервиса"
      title="Выйти"
      onClick={() => {
        void logout()
      }}
    >
      <LogOut {...ICON_PROPS} aria-hidden />
    </EmbedUiIconButton>
  )

  return (
    <div className={shellStyles.homeRoot}>
      <TrafficPageShell
        title="Управление дорожным движением"
        headerTrailing={headerTrailing}
        mapOverlay={<NotificationIcon />}
      />
    </div>
  )
}

export default function HomePage() {
  return (
    <RequireAuth>
      <HomeContent />
    </RequireAuth>
  )
}
