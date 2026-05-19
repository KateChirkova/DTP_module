"use client"

// layout: header + карта с overlay
import type { ReactNode } from "react"
import { Header } from "./header"
import MapWrapper from "./map-wrapper"
import styles from "./traffic-shell.module.css"

export type TrafficPageShellProps = {
  title?: ReactNode
  headerTrailing?: ReactNode
  mapOverlay?: ReactNode
}

export function TrafficPageShell({ title, headerTrailing, mapOverlay }: TrafficPageShellProps) {
  return (
    <main className={styles.pageShell}>
      <Header title={title} trailing={headerTrailing} />
      <div className={styles.pageShellMapArea}>
        <MapWrapper overlay={mapOverlay} />
      </div>
    </main>
  )
}

// устаревший алиас
export const TrafficMockPageShell = TrafficPageShell
