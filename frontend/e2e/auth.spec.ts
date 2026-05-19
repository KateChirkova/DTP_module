// E2E: редирект гостя, вход, неверный пароль
import { expect, test } from "@playwright/test"

import { E2E_LOGIN, E2E_PASSWORD, loginViaUi } from "./helpers"

test.describe("Авторизация (E2E)", () => {
  test("гость с / перенаправляется на /login", async ({ page }) => {
    await page.goto("/")
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByText("Управление дорожным движением")).toBeVisible()
  })

  test("успешный вход открывает главную", async ({ page }) => {
    await loginViaUi(page)
    await expect(page.getByRole("button", { name: "Выйти из сервиса" })).toBeVisible()
    await expect(page.getByLabel("Уведомления о ДТП")).toBeVisible()
  })

  test("неверный пароль показывает ошибку", async ({ page }) => {
    await page.goto("/login")
    await page.locator("#login").fill(E2E_LOGIN)
    await page.locator("#password").fill("wrong-password-e2e")
    await page.getByRole("button", { name: "Войти" }).click()

    await expect(page.locator('[role="alert"]').filter({ hasText: "Неверный логин или пароль" })).toBeVisible()
    await expect(page).toHaveURL(/\/login/)
  })

  test("выход возвращает на /login", async ({ page }) => {
    await loginViaUi(page)
    await page.getByRole("button", { name: "Выйти из сервиса" }).click()
    await expect(page).toHaveURL(/\/login/)
  })
})
