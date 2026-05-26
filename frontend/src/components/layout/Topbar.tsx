import { useNavigate } from 'react-router-dom'

import Button from '../common/Button'
import { useAuthStore } from '../../store/auth'

export default function Topbar() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const clear = useAuthStore((state) => state.clear)

  const handleLogout = () => {
    clear()
    navigate('/login')
  }

  return (
    <header className="flex items-center justify-between border-b border-surface-200 bg-white px-8 py-4">
      <div>
        <h2 className="text-sm font-semibold text-surface-900">Enterprise ESG Workspace</h2>
        <p className="text-xs text-surface-500">Ingestion status, review queue, and audit trail.</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right text-xs">
          <p className="font-semibold text-surface-800">{user?.username ?? 'Analyst'}</p>
          <p className="text-surface-500">{user?.organization?.name ?? 'Breathe ESG Demo'}</p>
        </div>
        <Button variant="ghost" onClick={handleLogout}>
          Sign out
        </Button>
      </div>
    </header>
  )
}
