// даты с API без TZ трактуем как UTC; отображение — Europe/Moscow
export function parseBackendDateAsUtc(value: string | null | undefined): Date | null {
  if (value == null) return null
  const s = String(value).trim()
  if (s === "") return null

  if (/[zZ]$/.test(s) || /[+-]\d{2}:?\d{2}$/.test(s)) {
    const d = new Date(s)
    return Number.isNaN(d.getTime()) ? null : d
  }

  const normalized = s.includes("T") ? s : s.replace(" ", "T")
  const d = new Date(`${normalized}Z`)
  return Number.isNaN(d.getTime()) ? null : d
}

const MOSCOW_TZ = "Europe/Moscow"

export function formatTimeMoscow(iso: string | null | undefined, fallback = "--:--"): string {
  const d = parseBackendDateAsUtc(iso)
  if (!d) return fallback
  return d.toLocaleTimeString("ru-RU", {
    timeZone: MOSCOW_TZ,
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function formatDateMoscow(iso: string | null | undefined): string {
  const d = parseBackendDateAsUtc(iso)
  if (!d) return ""
  return d.toLocaleDateString("ru-RU", { timeZone: MOSCOW_TZ })
}
