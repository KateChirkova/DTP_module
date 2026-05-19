// флаг dtp_auth для middleware (дополняет localStorage)
const AUTH_COOKIE = "dtp_auth"
const MAX_AGE_SEC = 60 * 60 * 24

export function setAuthCookie(): void {
  if (typeof document === "undefined") return
  document.cookie = `${AUTH_COOKIE}=1; path=/; max-age=${MAX_AGE_SEC}; SameSite=Lax`
}

export function clearAuthCookie(): void {
  if (typeof document === "undefined") return
  document.cookie = `${AUTH_COOKIE}=; path=/; max-age=0; SameSite=Lax`
}
