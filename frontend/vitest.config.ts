// vitest: тесты из tests/frontend, jsdom, алиасы @ и next
import path from "node:path"
import { fileURLToPath } from "node:url"

import react from "@vitejs/plugin-react"
import { defineConfig } from "vitest/config"

const frontendDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(frontendDir, "..")

const testGlob = `${repoRoot.replace(/\\/g, "/")}/tests/frontend/**/*.{test,spec}.{ts,tsx}`

export default defineConfig({
  root: frontendDir,
  server: {
    fs: {
      allow: [frontendDir, repoRoot],
    },
  },
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    include: [testGlob],
    setupFiles: [path.join(frontendDir, "vitest.setup.ts")],
    server: {
      deps: {
        inline: ["@testing-library/react", "@testing-library/jest-dom"],
      },
    },
  },
  resolve: {
    alias: {
      "@": frontendDir,
      "@testing-library/react": path.join(frontendDir, "node_modules/@testing-library/react"),
      "next/navigation": path.join(frontendDir, "node_modules/next/navigation.js"),
      "next/server": path.join(frontendDir, "node_modules/next/server.js"),
    },
  },
})
