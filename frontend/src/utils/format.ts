export const formatNumber = (value?: number | string | null, digits = 2) => {
  if (value === null || value === undefined) return '--'
  const parsed = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(parsed)) return '--'
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(parsed)
}

export const formatDate = (value?: string | null) => {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  }).format(date)
}

export const formatScope = (scope?: string | null) => {
  if (!scope) return '--'
  return scope.replace('_', ' ').toUpperCase()
}
