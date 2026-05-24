import { Filter, Film, Search, SlidersHorizontal } from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHeader } from '../components/PageHeader'

export function MoviesPage() {
  return (
    <div className="page-stack">
      <PageHeader
        title="Movies"
        description="Searchable catalog surface prepared for the backend movie list API."
      />

      <section className="toolbar" aria-label="Movie filters">
        <label className="input-shell">
          <Search size={18} aria-hidden="true" />
          <input type="search" placeholder="Search title" disabled />
        </label>
        <button className="button button--ghost" type="button" disabled>
          <Filter size={17} />
          Genre
        </button>
        <button className="button button--ghost" type="button" disabled>
          <SlidersHorizontal size={17} />
          Sort
        </button>
      </section>

      <section className="movie-grid-placeholder">
        <EmptyState
          icon={<Film size={32} />}
          title="Movie API pending"
          detail="The grid is ready for paged movie results from the backend."
        />
      </section>
    </div>
  )
}

