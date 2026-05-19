// мок useRouter / useSearchParams
import { vi } from "vitest"

const hoisted = vi.hoisted(() => ({
  mockRouter: {
    replace: vi.fn(),
    refresh: vi.fn(),
    push: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(),
  },
}))

export const mockRouter = hoisted.mockRouter

vi.mock("next/navigation", () => ({
  useRouter: () => mockRouter,
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}))
