import type { ReactNode } from 'react'

type StatusPanelProps = {
  icon: ReactNode
  title: string
  value: string
}

export function StatusPanel({ icon, title, value }: StatusPanelProps) {
  return (
    <article className="status-panel">
      <span className="status-panel__icon" aria-hidden="true">
        {icon}
      </span>
      <span className="status-panel__title">{title}</span>
      <strong>{value}</strong>
    </article>
  )
}

