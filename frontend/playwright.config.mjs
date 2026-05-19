// playwright: e2e против dev-сервера + API
import path from "node:path"
import { fileURLToPath } from "node:url"

import { defineConfig, devices } from "@playwright/test"

const frontendDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(frontendDir, "..")
const backendDir = path.join(repoRoot, "backend")

const apiBase = process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8080"
const webBase = process.env.PLAYWRIGHT_BASE_URL?.replace(/\/$/, "") || "http://localhost:3000"

export default defineConfig({
  testDir: path.join(frontendDir, "e2e"),
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 60_000,
  expect: {
    timeout: 15_000,
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.02,
      animations: "disabled",
    },
  },
  use: {
    baseURL: webBase,
    trace: "on-first-retry",
    viewport: { width: 1280, height: 720 },
    locale: "ru-RU",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "python -m uvicorn src.traffic_dtp.api.main:app --host 127.0.0.1 --port 8080",
      cwd: backendDir,
      url: `${apiBase}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        CORS_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000",
      },
    },
    {
      command: "npx next dev --hostname localhost --port 3000",
      cwd: frontendDir,
      url: webBase,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        NEXT_PUBLIC_API_BASE: apiBase,
      },
    },
  ],
})
