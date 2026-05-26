import clsx from 'clsx'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
  icon?: ReactNode
}

const variantStyles: Record<Variant, string> = {
  primary: 'bg-brand-600 text-white hover:bg-brand-700',
  secondary: 'bg-surface-900 text-white hover:bg-surface-800',
  ghost: 'bg-transparent text-surface-700 hover:bg-surface-100',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}

export default function Button({ variant = 'primary', className, icon, children, ...props }: Props) {
  return (
    <button
      className={clsx(
        'inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition',
        variantStyles[variant],
        className,
      )}
      {...props}
    >
      {icon}
      {children}
    </button>
  )
}
