import { useCallback, useMemo, useState } from 'react'

import { ToastContext, type ToastContextValue, type ToastVariant } from './ToastContext'

type Toast = {
  id: string
  message: string
  variant: ToastVariant
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const notify = useCallback((message: string, variant: ToastVariant = 'info') => {
    const id = crypto.randomUUID()
    setToasts((current) => [...current, { id, message, variant }])
    setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id))
    }, 4000)
  }, [])

  const value: ToastContextValue = useMemo(() => ({ notify }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-6 top-6 z-50 flex flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={[
              'rounded-xl px-4 py-3 text-sm font-semibold shadow-card',
              toast.variant === 'success' && 'bg-emerald-600 text-white',
              toast.variant === 'error' && 'bg-red-600 text-white',
              toast.variant === 'info' && 'bg-surface-900 text-white',
            ]
              .filter(Boolean)
              .join(' ')}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
