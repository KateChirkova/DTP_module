// тесты dismissAllToasts
import { describe, expect, it, vi } from "vitest"

import { dismissAllToasts, registerToastDismiss } from "@/lib/ui-events"

describe("ui-events", () => {
  it("registerToastDismiss и dismissAllToasts", () => {
    const dismiss = vi.fn()
    const unregister = registerToastDismiss(dismiss)
    dismissAllToasts()
    expect(dismiss).toHaveBeenCalledOnce()
    unregister()
    dismiss.mockClear()
    dismissAllToasts()
    expect(dismiss).not.toHaveBeenCalled()
  })
})
