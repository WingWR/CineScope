import { Sparkles } from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHeader } from '../components/PageHeader'

export function RecommendationsPage() {
  return (
    <div className="page-stack">
      <PageHeader
        title="Recommendations"
        description="Reserved for recommendation results from algorithm and backend services."
      />

      <section className="panel panel--wide">
        <EmptyState
          icon={<Sparkles size={32} />}
          title="Recommendation API pending"
          detail="Personalized and item-to-item results will mount here after the API contract is available."
        />
      </section>
    </div>
  )
}

