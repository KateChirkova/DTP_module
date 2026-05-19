"use client"

import { Loader2 } from "lucide-react"
import type { ReactNode } from "react"

type PageSpinnerProps = {
  message?: string
  footer?: ReactNode
}

export function PageSpinner({ message = "Загрузка…", footer }: PageSpinnerProps) {
  return (
    <div className="flex min-h-[100dvh] w-full flex-col items-center justify-center gap-3 bg-zinc-100 p-4 text-slate-900">
      <Loader2 className="h-9 w-9 animate-spin text-slate-500" aria-hidden />
      <p className="m-0 text-center text-sm text-slate-500">{message}</p>
      {footer}
    </div>
  )
}
