// сброс всех toast при открытии drawer (регистрирует Toaster)
let toastDismiss: (() => void) | null = null

export function registerToastDismiss(fn: () => void): () => void {
  toastDismiss = fn
  return () => {
    if (toastDismiss === fn) {
      toastDismiss = null
    }
  }
}

export function dismissAllToasts() {
  toastDismiss?.()
}
