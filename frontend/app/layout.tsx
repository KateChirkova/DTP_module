import "../globals.css"

import AccidentNotifications from "@/hooks/accident-notifications"
import { Toaster } from "@/components/ui/toaster"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        {children}
        <AccidentNotifications />  // ✅ Только 1 WS!
        <Toaster />
      </body>
    </html>
  )
}