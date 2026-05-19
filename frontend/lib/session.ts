import { apiFetch } from "@/lib/http"

// проверка Bearer-токена на бэкенде
export async function verifySessionToken(token: string): Promise<string | null> {
  const result = await apiFetch<{ success?: boolean; login?: string }>(
    "/api/v1/auth/verify",
    { token, skipSessionExpired: true },
  )
  if (!result.ok) return null
  return result.data.login ?? null
}
