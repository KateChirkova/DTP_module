"use client"

import type { ReactNode } from "react"
import { Camera, FileDown } from "lucide-react"
import { EmbedUiIconButton } from "./EmbedUiIconButton"
import styles from "./traffic-chrome.module.css"

export type TrafficKrasnodarHeaderDecorProps = {
  trailing?: ReactNode
}

// декоративные кнопки как в traffic_krasnodar (без бизнес-логики)
export function TrafficKrasnodarHeaderDecor({ trailing }: TrafficKrasnodarHeaderDecorProps) {
  return (
    <div
      className={styles.actionRow}
      style={{
        display: "flex",
        flexWrap: "nowrap",
        alignItems: "center",
        justifyContent: "flex-end",
        gap: 8,
        flexShrink: 0,
      }}
    >
      <EmbedUiIconButton
        type="button"
        aria-label="Снимок экрана (макет интерфейса)"
        title="Снимок экрана — только оформление"
        onClick={(e) => {
          e.preventDefault()
        }}
      >
        <Camera width={16} height={16} aria-hidden />
      </EmbedUiIconButton>
      <EmbedUiIconButton
        type="button"
        aria-label="Экспорт (макет интерфейса)"
        title="Экспорт — только оформление"
        onClick={(e) => {
          e.preventDefault()
        }}
      >
        <FileDown width={16} height={16} aria-hidden />
      </EmbedUiIconButton>
      {trailing}
    </div>
  )
}
