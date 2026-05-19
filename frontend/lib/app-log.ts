// лог [DTP] в консоль (prod и dev)
const PREFIX = "[DTP]"

export function logAppError(scope: string, detail?: unknown): void {
  if (detail !== undefined) {
    console.error(PREFIX, scope, detail)
  } else {
    console.error(PREFIX, scope)
  }
}

export function logAppWarn(scope: string, detail?: unknown): void {
  if (detail !== undefined) {
    console.warn(PREFIX, scope, detail)
  } else {
    console.warn(PREFIX, scope)
  }
}
