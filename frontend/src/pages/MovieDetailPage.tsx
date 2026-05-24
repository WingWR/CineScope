import { ArrowLeft, Clapperboard, Star, Tags } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'

export function MovieDetailPage() {
  const { movieId } = useParams()

  return (
    <div className="page-stack">
      <Link className="back-link" to="/movies">
        <ArrowLeft size={17} />
        Movies
      </Link>

      <section className="detail-hero">
        <div className="detail-hero__poster" aria-hidden="true">
          <Clapperboard size={54} />
        </div>
        <div>
          <span className="eyebrow">Movie ID {movieId}</span>
          <h1>Detail API pending</h1>
          <p>Title, overview, media, ratings, and tags will render from the movie detail endpoint.</p>
        </div>
      </section>

      <section className="content-grid content-grid--two">
        <div className="panel">
          <EmptyState
            icon={<Star size={28} />}
            title="Ratings pending"
            detail="MovieLens and TMDb score fields will appear here."
          />
        </div>
        <div className="panel">
          <EmptyState
            icon={<Tags size={28} />}
            title="Tags pending"
            detail="Top user tags and genre metadata will appear here."
          />
        </div>
      </section>
    </div>
  )
}

