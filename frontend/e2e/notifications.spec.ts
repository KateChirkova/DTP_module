// E2E: drawer уведомлений после входа
import { expect, test } from "@playwright/test"

import { loginViaUi } from "./helpers"

test.describe("Панель уведомлений (E2E)", () => {
  test.beforeEach(async ({ page }) => {
    await loginViaUi(page)
  })

  test("открытие drawer по FAB", async ({ page }) => {
    await page.getByLabel("Уведомления о ДТП").click()
    await expect(page.locator(".dtp-drawer__title")).toHaveText("Уведомления")
    await expect(page.locator(".dtp-drawer__markall")).toBeVisible()
  })

  test("повторное открытие drawer после закрытия", async ({ page }) => {
    const fab = page.getByLabel("Уведомления о ДТП")
    await fab.click()
    await expect(page.locator(".dtp-drawer")).toBeVisible()

    await page.keyboard.press("Escape")
    await expect(page.locator(".dtp-drawer")).toBeHidden({ timeout: 10_000 })

    await fab.click()
    await expect(page.locator(".dtp-drawer__title")).toBeVisible()
  })
})
