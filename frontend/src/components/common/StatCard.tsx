type StatCardProps = {
  label: string
  value: string
  helper?: string
}

export default function StatCard({ label, value, helper }: StatCardProps) {
  return (
    <div className="card flex flex-col gap-2">
      <span className="text-xs font-semibold uppercase tracking-wide text-surface-500">{label}</span>
      <span className="text-2xl font-semibold text-surface-900">{value}</span>
      {helper ? <span className="text-xs text-surface-500">{helper}</span> : null}
    </div>
  )
}
