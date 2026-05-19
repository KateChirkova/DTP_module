// E2E: скриншот-regression (login, home, drawer)
import { expect, test } from "@playwright/test"

import { loginViaUi } from "./helpers"

test.describe("Визуальные снапшоты", () => {
  test("страница входа", async ({ page }) => {
    await page.goto("/login")
    await expect(page.locator(".dtp-login-page")).toBeVisible()
    await expect(page.locator(".dtp-login-page")).toHaveScreenshot("login-page.png", {
      maxDiffPixelRatio: 0.03,
    })
  })

  test("FAB на главной", async ({ page }) => {
    await loginViaUi(page)
    const fab = page.locator(".dtp-fab")
    await expect(fab).toBeVisible()
    await expect(fab).toHaveScreenshot("fab.png", {
      maxDiffPixelRatio: 0.03,
    })
  })

  test("drawer уведомлений", async ({ page }) => {
    await loginViaUi(page)
    await page.getByLabel("Уведомления о ДТП").click()
    const drawer = page.locator(".dtp-drawer")
    await expect(drawer).toBeVisible()
    await expect(drawer).toHaveScreenshot("notifications-drawer.png", {
      maxDiffPixelRatio: 0.03,
      mask: [page.locator(".dtp-drawer__list")],
    })
  })

  test("главная (карта замаскирована)", async ({ page }) => {
    await loginViaUi(page)
    await expect(page.locator("main")).toBeVisible()
    await expect(page).toHaveScreenshot("home-page.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.04,
      mask: [page.locator("iframe")],
    })
  })
})
