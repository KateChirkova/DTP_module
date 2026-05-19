"use client"

// кнопка-иконка в стиле traffic_krasnodar
import * as React from "react"
import styles from "./traffic-chrome.module.css"

export type EmbedUiIconButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>

export const EmbedUiIconButton = React.forwardRef<HTMLButtonElement, EmbedUiIconButtonProps>(
  ({ className, children, type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={[styles.iconBtn, className].filter(Boolean).join(" ")}
      {...props}
    >
      {children}
    </button>
  ),
)
EmbedUiIconButton.displayName = "EmbedUiIconButton"
