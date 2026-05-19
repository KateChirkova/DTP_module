// тесты демо-оверлея на карте
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { DtpMapOverlayDemo } from "@/components/dtp-on-map/DtpMapOverlayDemo"

describe("DtpMapOverlayDemo", () => {
  it("рендерит FAB и demo drawer", async () => {
    render(<DtpMapOverlayDemo />)

    const btn = screen.getByRole("button", { name: /демо/i })
    expect(btn).toBeInTheDocument()

    fireEvent.click(btn)

    expect(await screen.findByText(/Демо:/)).toBeInTheDocument()
  })
})
