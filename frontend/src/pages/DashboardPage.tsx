import { BarChart3, Film, Server, Star, Tags, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { PageHeader } from '../components/PageHeader'
import { StatusPanel } from '../components/StatusPanel'
import { isApiConfigured } from '../api/client'

const summaryPanels = [
  { title: 'Movies', icon: Film },
  { title: 'Ratings', icon: Star },
  { title: 'Tags', icon: Tags },
  { title: 'Users', icon: Users },
]

export function DashboardPage() {
  const apiReady = isApiConfigured()

  return (
    <div className="page-stack">
      <section className="hero-band">
        <PageHeader
          title="CineScope"
          description="Movie catalog intelligence for search, analysis, and recommendation workflows."
          action={
            <Link className="button button--primary" to="/movies">
              Browse Movies
            </Link>
          }
        />
      </section>

      <section className="summary-grid" aria-label="Dataset summary">
        {summaryPanels.map(({ title, icon: Icon }) => (
          <StatusPanel
            key={title}
            title={title}
            value={apiReady ? 'Loading' : 'API pending'}
            icon={<Icon size={20} strokeWidth={2.2} />}
          />
        ))}
      </section>

      <section className="content-grid content-grid--two">
        <div className="panel">
          <div className="panel__header">
            <h2>Top Rated</h2>
            <Link to="/movies">View all</Link>
          </div>
          <EmptyState
            icon={<Star size={28} />}
            title="Ranking API pending"
            detail="This panel is reserved for backend-provided top rated movies."
          />
        </div>

        <div className="panel">
          <div className="panel__header">
            <h2>Genre Coverage</h2>
            <Link to="/genres">Open genres</Link>
          </div>
          <EmptyState
            icon={<BarChart3 size={28} />}
            title="Stats API pending"
            detail="Genre distribution will render after the backend exposes dataset statistics."
          />
        </div>
      </section>

      <section className="panel panel--wide">
        <EmptyState
          icon={<Server size={28} />}
          title="Backend connection not configured"
          detail="Set VITE_API_BASE_URL when the service is ready."
        />
      </section>
    </div>
  )
}

