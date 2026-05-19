// console.log/warn только в development
const isDev = process.env.NODE_ENV === "development"

export function devLog(...args: unknown[]): void {
  if (isDev) console.log(...args)
}

export function devWarn(...args: unknown[]): void {
  if (isDev) console.warn(...args)
}
