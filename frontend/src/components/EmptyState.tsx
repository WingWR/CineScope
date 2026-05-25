import type { ReactNode } from 'react'

type EmptyStateProps = {
  icon: ReactNode
  title: string
  detail: string
  action?: ReactNode
}

export function EmptyState({ icon, title, detail, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon" aria-hidden="true">
        {icon}
      </div>
      <div>
        <h2>{title}</h2>
        <p>{detail}</p>
      </div>
      {action}
    </div>
  )
}

