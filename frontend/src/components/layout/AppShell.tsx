import { useQuery } from '@tanstack/react-query'
import { Outlet } from 'react-router-dom'

import Sidebar from './Sidebar'
import Topbar from './Topbar'
import { fetchMe } from '../../services/auth'
import { useAuthStore } from '../../store/auth'

export default function AppShell() {
  const token = useAuthStore((state) => state.accessToken)
  const user = useAuthStore((state) => state.user)

  useQuery({
    queryKey: ['me'],
    queryFn: fetchMe,
    enabled: Boolean(token && !user),
  })

  return (
    <div className="flex min-h-screen bg-surface-50">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 space-y-6 px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
