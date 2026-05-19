// render с AuthProvider / NotificationsProvider
import { render, type RenderOptions } from "@testing-library/react"
import type { ReactElement, ReactNode } from "react"

import { AuthProvider } from "@/contexts/AuthContext"
import { NotificationsProvider } from "@/contexts/NotificationsContext"

export {
  jsonResponse,
  mockFetch,
  mockRouter,
  seedSession,
} from "./test-utils-fetch"

type WrapperOptions = {
  withAuth?: boolean
  withNotifications?: boolean
}

export function createAppWrapper(options?: WrapperOptions) {
  const { withAuth = true, withNotifications = true } = options ?? {}
  return function Wrapper({ children }: { children: ReactNode }) {
    if (withAuth && withNotifications) {
      return (
        <AuthProvider>
          <NotificationsProvider>{children}</NotificationsProvider>
        </AuthProvider>
      )
    }
    if (withNotifications) {
      return <NotificationsProvider>{children}</NotificationsProvider>
    }
    return <>{children}</>
  }
}

export function renderWithProviders(
  ui: ReactElement,
  options?: RenderOptions & WrapperOptions,
) {
  const { withAuth, withNotifications, ...renderOptions } = options ?? {}
  const wrapper = createAppWrapper({ withAuth, withNotifications })
  return render(ui, { wrapper, ...renderOptions })
}
