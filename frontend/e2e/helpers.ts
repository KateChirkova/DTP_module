import type { Page } from "@playwright/test"

export const E2E_LOGIN = process.env.DTP_E2E_LOGIN ?? "admin"
export const E2E_PASSWORD = process.env.DTP_E2E_PASSWORD ?? "admin123"

// логин через UI (нужен живой API)
export async function loginViaUi(page: Page, login = E2E_LOGIN, password = E2E_PASSWORD) {
  await page.goto("/login")
  await page.locator("#login").fill(login)
  await page.locator("#password").fill(password)
  await page.getByRole("button", { name: "Войти" }).click()
  await page.waitForURL((url) => url.pathname === "/", { timeout: 30_000 })
}
