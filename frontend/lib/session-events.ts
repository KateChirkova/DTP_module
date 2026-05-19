// глобальный callback при 401 (logout + redirect)
let onSessionExpired: (() => void) | null = null

export function setSessionExpiredHandler(handler: (() => void) | null) {
  onSessionExpired = handler
}

export function notifySessionExpired() {
  onSessionExpired?.()
}
