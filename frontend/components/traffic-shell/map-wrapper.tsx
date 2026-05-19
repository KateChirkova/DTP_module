"use client"

// iframe Яндекс.Карт + слот overlay (FAB, демо)
import type { ReactNode } from "react"

import styles from "./traffic-shell.module.css"

const YANDEX_MAP_WIDGET_SRC =
  "https://yandex.ru/map-widget/v1/?um=constructor%3Ac52db986d8148a57acd7f6f0af9791aacdd1675b4e6fe5eedb315d84d7cde46b&source=constructor"

export type MapWrapperProps = {
  overlay?: ReactNode
}

export default function MapWrapper({ overlay }: MapWrapperProps) {
  return (
    <div className={styles.trafficMockMap}>
      <iframe
        className={styles.mapIframe}
        src={YANDEX_MAP_WIDGET_SRC}
        title="Яндекс Карта"
        allow="geolocation"
      />
      {overlay}
    </div>
  )
}
