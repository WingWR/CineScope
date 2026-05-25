import { Clapperboard } from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'

export function NotFoundPage() {
  return (
    <div className="page-stack">
      <section className="panel panel--wide">
        <EmptyState
          icon={<Clapperboard size={32} />}
          title="Page not found"
          detail="The requested CineScope route does not exist."
          action={
            <Link className="button button--primary" to="/">
              Back to Overview
            </Link>
          }
        />
      </section>
    </div>
  )
}

