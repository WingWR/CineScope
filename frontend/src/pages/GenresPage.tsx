import { BarChart3, Tags } from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHeader } from '../components/PageHeader'

export function GenresPage() {
  return (
    <div className="page-stack">
      <PageHeader title="Genres" description="MovieLens genre distribution and navigation entry points." />

      <section className="panel panel--wide">
        <EmptyState
          icon={<BarChart3 size={30} />}
          title="Genre stats API pending"
          detail="The chart area is reserved for genre distribution returned by the backend."
        />
      </section>

      <section className="genre-strip" aria-label="Genre filters pending">
        {['Action', 'Comedy', 'Drama', 'Thriller', 'Sci-Fi', 'Romance'].map((genre) => (
          <button className="chip" type="button" disabled key={genre}>
            <Tags size={14} />
            {genre}
          </button>
        ))}
      </section>
    </div>
  )
}

