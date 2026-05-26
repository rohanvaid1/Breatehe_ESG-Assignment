import { useMutation } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'

import Button from '../components/common/Button'
import useToast from '../components/common/useToast'
import { login, fetchMe } from '../services/auth'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { notify } = useToast()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const mutation = useMutation({
    mutationFn: async () => {
      await login(username, password)
      await fetchMe()
    },
    onSuccess: () => {
      notify('Signed in successfully.', 'success')
      const redirectTo = (location.state as { from?: Location })?.from?.pathname ?? '/dashboard'
      navigate(redirectTo, { replace: true })
    },
    onError: () => notify('Login failed. Check credentials.', 'error'),
  })

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 px-6">
      <div className="w-full max-w-md space-y-6 rounded-3xl border border-surface-200 bg-white p-8 shadow-card">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900">Breathe ESG</h1>
          <p className="text-sm text-surface-500">
            Sign in to manage ingestion, review anomalies, and approve data.
          </p>
        </div>
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault()
            mutation.mutate()
          }}
        >
          <div className="space-y-2">
            <label className="text-xs font-semibold text-surface-600">Username</label>
            <input
              className="w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="analyst"
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-semibold text-surface-600">Password</label>
            <input
              className="w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              placeholder="••••••••"
              required
            />
          </div>
          <Button className="w-full" disabled={mutation.isPending}>
            {mutation.isPending ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>
        <div className="rounded-xl bg-surface-100 p-4 text-xs text-surface-600">
          Demo credentials: <span className="font-semibold">analyst / breathe123</span>
        </div>
      </div>
    </div>
  )
}
