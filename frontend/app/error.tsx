"use client"

// граница ошибок сегмента App Router (без неё dev может зациклиться)
export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div
      style={{
        boxSizing: "border-box",
        minHeight: "100dvh",
        padding: 24,
        fontFamily: "system-ui, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
        background: "#f8fafc",
        color: "#0f172a",
      }}
    >
      <h1 style={{ fontSize: 18, margin: 0 }}>Ошибка</h1>
      <p style={{ margin: 0, fontSize: 14, color: "#64748b", textAlign: "center", maxWidth: 420 }}>
        {error.message || "Неизвестная ошибка"}
      </p>
      <button
        type="button"
        onClick={() => reset()}
        style={{
          padding: "10px 18px",
          fontSize: 14,
          cursor: "pointer",
          borderRadius: 8,
          border: "1px solid #cbd5e1",
          background: "#fff",
        }}
      >
        Попробовать снова
      </button>
    </div>
  )
}