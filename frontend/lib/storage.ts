// безопасный localStorage (приватный режим / блокировка)
export function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export function writeStorage(key: string, value: string): void {
  try {
    localStorage.setItem(key, value)
  } catch {
    // storage может быть недоступен
  }
}

export function clearStorage(): void {
  try {
    localStorage.clear()
  } catch {
    // ignore
  }
}
