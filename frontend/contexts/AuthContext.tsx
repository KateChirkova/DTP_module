"use client"

// сессия: localStorage + cookie + /auth/verify; глобальный logout при 401
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { PageSpinner } from "@/components/ui/page-spinner"

import { setAuthCookie, clearAuthCookie } from "@/lib/auth-cookie"
import { logAppError } from "@/lib/app-log"
import { devLog, devWarn } from "@/lib/dev-log"
import { apiFetch } from "@/lib/http"
import { setSessionExpiredHandler } from "@/lib/session-events"
import { verifySessionToken } from "@/lib/session"
import { clearStorage, readStorage, writeStorage } from "@/lib/storage"
import { dismissAllToasts } from "@/lib/ui-events"

interface AuthState {
  user: string | null
  token: string | null
  isLoading: boolean
  isValid: boolean
}

export type LoginResult =
  | { ok: true }
  | { ok: false; reason: "invalid" | "network" | "server" }

interface AuthContextType {
  auth: AuthState
  login: (login: string, password: string) => Promise<LoginResult>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

const emptyAuth: AuthState = {
  user: null,
  token: null,
  isLoading: false,
  isValid: false,
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({ ...emptyAuth, isLoading: true })
  const router = useRouter()

  const clearLocalSession = useCallback(() => {
    clearStorage()
    clearAuthCookie()
    setAuth(emptyAuth)
    dismissAllToasts()
  }, [])

  useEffect(() => {
    setSessionExpiredHandler(() => {
      clearLocalSession()
      router.replace("/login?reset=1")
    })
    return () => setSessionExpiredHandler(null)
  }, [clearLocalSession, router])

  useEffect(() => {
    const init = async () => {
      const token = readStorage("token")
      if (!token) {
        clearAuthCookie()
        setAuth(emptyAuth)
        return
      }

      const storedUser = readStorage("user")

      try {
        devLog("Проверка сессии...")
        const loginName = await verifySessionToken(token)
        if (loginName) {
          writeStorage("user", loginName)
          setAuthCookie()
          setAuth({ user: loginName, token, isLoading: false, isValid: true })
          return
        }

        clearLocalSession()
      } catch (error) {
        const name = error instanceof Error ? error.name : ""
        const isNetwork =
          name === "AbortError" ||
          (error instanceof TypeError &&
            String(error.message).toLowerCase().includes("fetch"))

        // офлайн: доверяем локальной сессии до следующей проверки
        if (isNetwork && storedUser && token) {
          devWarn("Сеть недоступна — локальная сессия до следующей проверки")
          setAuthCookie()
          setAuth({ user: storedUser, token, isLoading: false, isValid: true })
          return
        }

        logAppError("auth.verify", error)
        clearLocalSession()
      }
    }

    void init().catch((err) => {
      logAppError("auth.init", err)
      clearLocalSession()
    })
  }, [clearLocalSession])

  const login = async (loginName: string, password: string): Promise<LoginResult> => {
    let result:
      | { ok: true; data: { token?: string; user?: string; login?: string } }
      | { ok: false; status: number }
    try {
      result = await apiFetch<{ token?: string; user?: string; login?: string }>(
        "/api/v1/auth/login",
        {
          method: "POST",
          body: { login: loginName, password },
          skipSessionExpired: true,
        },
      )
    } catch {
      return { ok: false, reason: "network" }
    }

    if (!result.ok) {
      if (result.status === 401 || result.status === 403) {
        return { ok: false, reason: "invalid" }
      }
      if (result.status >= 500) {
        return { ok: false, reason: "server" }
      }
      return { ok: false, reason: "network" }
    }

    const data = result.data
    const userLogin = data.user ?? data.login ?? null
    const name = typeof userLogin === "string" ? userLogin.trim() : ""
    if (!data.token || !name) {
      logAppError("auth.login.invalidPayload", data)
      clearLocalSession()
      return { ok: false, reason: "server" }
    }

    writeStorage("token", data.token)
    writeStorage("user", name)
    setAuthCookie()
    setAuth({ user: name, token: data.token, isLoading: false, isValid: true })
    devLog("Логин успешен")
    return { ok: true }
  }

  const logout = useCallback(() => {
    const token = readStorage("token")
    clearLocalSession()
    router.replace("/login?reset=1")
    router.refresh()

    if (token) {
      void apiFetch("/api/v1/auth/logout", {
        token,
        method: "POST",
        skipSessionExpired: true,
      })
    }
  }, [clearLocalSession, router])

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth нужно вызывать внутри AuthProvider")
  }
  return context
}

// защита страницы после middleware
export function RequireAuth({ children }: { children: ReactNode }) {
  const { auth } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (auth.isLoading) return
    if (!auth.isValid || !auth.user) {
      router.replace("/login")
    }
  }, [auth.isLoading, auth.isValid, auth.user, router])

  if (auth.isLoading || !auth.isValid || !auth.user) {
    const showManualLogin = !auth.isLoading && (!auth.isValid || !auth.user)
    return (
      <PageSpinner
        message={auth.isLoading ? "Проверка сессии…" : "Перенаправление на вход…"}
        footer={
          showManualLogin ? (
            <Link href="/login" className="text-sm font-semibold text-sky-700 underline">
              Перейти ко входу
            </Link>
          ) : null
        }
      />
    )
  }

  return <>{children}</>
}
