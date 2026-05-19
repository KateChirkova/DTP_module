// корень приложения: auth, уведомления, WS-toast
import "../globals.css"
import AccidentNotifications from "@/hooks/accident-notifications"
import { Toaster } from "@/components/ui/toaster"
import { AuthProvider } from "@/contexts/AuthContext"
import { NotificationsProvider } from "@/contexts/NotificationsContext"
import { Inter } from "next/font/google"

const inter = Inter({ subsets: ["latin", "cyrillic"] })

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body
        className={`${inter.className} min-h-screen bg-background text-foreground app-body-layout`}
      >
        <AuthProvider>
          <NotificationsProvider>
            <div className="app-viewport">{children}</div>
            <AccidentNotifications />
            <Toaster />
          </NotificationsProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
