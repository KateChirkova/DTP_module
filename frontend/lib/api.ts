// базовый URL API (NEXT_PUBLIC_API_BASE при сборке)
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8080"
