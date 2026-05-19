"use client"

// шапка страницы: заголовок + декор traffic_krasnodar
import type { ReactNode } from "react"
import { TrafficKrasnodarHeaderDecor } from "@/modules/embed-ui"
import styles from "./traffic-shell.module.css"

export type TrafficHeaderProps = {
  title?: ReactNode
  trailing?: ReactNode
}

export function Header({ title = "Управление дорожным движением", trailing }: TrafficHeaderProps) {
  return (
    <div className={styles.trafficMockHeaderBar}>
      <div className={styles.headerRowLeft}>
        <h1 className={styles.trafficMockTitle}>{title}</h1>
      </div>
      <div className={styles.headerRightCluster}>
        <TrafficKrasnodarHeaderDecor trailing={trailing} />
      </div>
    </div>
  )
}
