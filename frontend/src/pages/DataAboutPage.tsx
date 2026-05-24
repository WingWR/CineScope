import { Database, ShieldCheck } from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHeader } from '../components/PageHeader'

export function DataAboutPage() {
  return (
    <div className="page-stack">
      <PageHeader
        title="Data"
        description="Dataset lineage, field contract, and quality checkpoints for the CineScope catalog."
      />

      <section className="content-grid content-grid--two">
        <div className="panel">
          <EmptyState
            icon={<Database size={28} />}
            title="Summary API pending"
            detail="Dataset summary will come from the backend stats endpoint."
          />
        </div>
        <div className="panel">
          <EmptyState
            icon={<ShieldCheck size={28} />}
            title="Quality API pending"
            detail="Quality report fields are reserved for service-side publication."
          />
        </div>
      </section>
    </div>
  )
}

