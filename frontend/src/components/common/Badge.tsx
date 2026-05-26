import clsx from 'clsx'

type BadgeVariant = 'success' | 'warning' | 'danger' | 'neutral' | 'info'

const badgeStyles: Record<BadgeVariant, string> = {
  success: 'bg-emerald-100 text-emerald-700',
  warning: 'bg-amber-100 text-amber-700',
  danger: 'bg-red-100 text-red-700',
  neutral: 'bg-surface-100 text-surface-600',
  info: 'bg-blue-100 text-blue-700',
}

export default function Badge({ label, variant = 'neutral' }: { label: string; variant?: BadgeVariant }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold',
        badgeStyles[variant],
      )}
    >
      {label}
    </span>
  )
}
