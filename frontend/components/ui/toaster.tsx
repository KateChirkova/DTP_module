"use client";

// рендер очереди toast; регистрирует dismissAllToasts
import { useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { registerToastDismiss } from "@/lib/ui-events"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  useEffect(() => registerToastDismiss(dismiss), [dismiss])

  return (
    <ToastProvider duration={30000}>
      {toasts.map(function ({ id, title, description, action, ...props }) {
        return (
          <Toast key={id} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
