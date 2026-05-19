// тесты reducer toast
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { reducer } from "@/hooks/use-toast"

const baseToast = {
  id: "1",
  open: true,
  title: "ДТП",
}

describe("use-toast reducer", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("ADD_TOAST добавляет toast в начало", () => {
    const next = reducer({ toasts: [] }, { type: "ADD_TOAST", toast: baseToast })
    expect(next.toasts).toHaveLength(1)
    expect(next.toasts[0].id).toBe("1")
  })

  it("ADD_TOAST ограничивает список пятью элементами", () => {
    let state = { toasts: [] as typeof baseToast[] }
    for (let i = 0; i < 7; i++) {
      state = reducer(state, {
        type: "ADD_TOAST",
        toast: { ...baseToast, id: String(i) },
      })
    }
    expect(state.toasts).toHaveLength(5)
    expect(state.toasts[0].id).toBe("6")
  })

  it("UPDATE_TOAST обновляет поля по id", () => {
    const state = reducer(
      { toasts: [baseToast] },
      { type: "UPDATE_TOAST", toast: { id: "1", title: "Обновлено" } },
    )
    expect(state.toasts[0].title).toBe("Обновлено")
  })

  it("DISMISS_TOAST помечает toast закрытым", () => {
    const state = reducer(
      { toasts: [baseToast] },
      { type: "DISMISS_TOAST", toastId: "1" },
    )
    expect(state.toasts[0].open).toBe(false)
  })

  it("REMOVE_TOAST удаляет по id", () => {
    const state = reducer(
      { toasts: [baseToast, { ...baseToast, id: "2" }] },
      { type: "REMOVE_TOAST", toastId: "1" },
    )
    expect(state.toasts).toHaveLength(1)
    expect(state.toasts[0].id).toBe("2")
  })

  it("REMOVE_TOAST без id очищает все", () => {
    const state = reducer(
      { toasts: [baseToast, { ...baseToast, id: "2" }] },
      { type: "REMOVE_TOAST" },
    )
    expect(state.toasts).toHaveLength(0)
  })
})
