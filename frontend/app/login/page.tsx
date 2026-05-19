"use client"

// форма входа; redirect после успеха или ?reset=1
import { Suspense, useState, useTransition, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { PageSpinner } from "@/components/ui/page-spinner"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

function LoginForm() {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState("")
  const router = useRouter()
  const searchParams = useSearchParams()
  const { auth, login: authLogin } = useAuth()

  useEffect(() => {
    if (searchParams.get("reset") === "1") {
      setLogin("")
      setPassword("")
      setError("")
      router.replace("/login")
    }
  }, [searchParams, router])

  useEffect(() => {
    if (auth.isValid && !auth.isLoading && auth.user) {
      router.replace("/")
    }
  }, [auth.isValid, auth.isLoading, auth.user, router])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    startTransition(async () => {
      const result = await authLogin(login, password)
      if (result.ok) {
        router.replace("/")
        return
      }
      if (result.reason === "network") {
        setError("Сервер недоступен. Проверьте, что API запущен.")
      } else if (result.reason === "server") {
        setError("Ошибка сервера. Попробуйте позже.")
      } else {
        setError("Неверный логин или пароль")
      }
    })
  }

  if (auth.isLoading) {
    return <PageSpinner message="Загрузка…" />
  }

  if (auth.isValid && auth.user) {
    return <PageSpinner message="Перенаправление…" />
  }

  return (
    <div className="dtp-login-page text-foreground">
      <Card className="w-full max-w-md border bg-card text-card-foreground shadow-md">
        <CardHeader className="space-y-1 pb-4">
          <CardTitle className="text-center text-2xl font-semibold tracking-tight">
            Управление дорожным движением
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="login" className="text-sm font-medium leading-none">
                Логин
              </label>
              <Input
                id="login"
                type="text"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                placeholder="Введите логин"
                disabled={isPending}
                autoComplete="username"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none">
                Пароль
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Введите пароль"
                disabled={isPending}
                autoComplete="current-password"
              />
            </div>

            {error ? (
              <div
                role="alert"
                className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-center text-sm font-medium text-destructive"
              >
                {error}
              </div>
            ) : null}

            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? "Входим..." : "Войти"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

function LoginFallback() {
  return <PageSpinner />
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginFallback />}>
      <LoginForm />
    </Suspense>
  )
}
