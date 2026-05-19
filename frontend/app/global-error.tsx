"use client"

// ошибки корневого layout; свои html/body обязательны для Next.js
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="ru">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", padding: 24 }}>
        <h1 style={{ fontSize: 18 }}>Критическая ошибка</h1>
        <p style={{ color: "#64748b", fontSize: 14 }}>{error.message || "Неизвестная ошибка"}</p>
        <button type="button" onClick={() => reset()} style={{ marginTop: 12, padding: "8px 16px" }}>
          Снова
        </button>
      </body>
    </html>
  )
}
