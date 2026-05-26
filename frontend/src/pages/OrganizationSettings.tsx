import { useQuery } from '@tanstack/react-query'

import Table from '../components/common/Table'
import api from '../services/apiClient'
import type { Organization, User } from '../types'
import { unwrapList } from '../utils/api'

export default function OrganizationSettings() {
  const orgQuery = useQuery({
    queryKey: ['organizations'],
    queryFn: async (): Promise<Organization[]> => {
      const response = await api.get('/organizations/')
      return unwrapList<Organization>(response.data)
    },
  })

  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: async (): Promise<User[]> => {
      const response = await api.get('/users/')
      return unwrapList<User>(response.data)
    },
  })

  const organization = orgQuery.data?.[0]

  return (
    <div className="space-y-6">
      <div className="card space-y-2">
        <h3 className="text-sm font-semibold text-surface-900">Organization profile</h3>
        <p className="text-xs text-surface-500">Tenant context for ingestion and approvals.</p>
        {organization ? (
          <div className="grid gap-4 text-sm text-surface-700 md:grid-cols-2">
            <div>
              <span className="text-xs text-surface-500">Name</span>
              <p className="font-semibold">{organization.name}</p>
            </div>
            <div>
              <span className="text-xs text-surface-500">Industry</span>
              <p className="font-semibold">{organization.industry || '—'}</p>
            </div>
            <div>
              <span className="text-xs text-surface-500">Country</span>
              <p className="font-semibold">{organization.country || '—'}</p>
            </div>
            <div>
              <span className="text-xs text-surface-500">Timezone</span>
              <p className="font-semibold">{organization.timezone || 'UTC'}</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-surface-500">No organization configured yet.</p>
        )}
      </div>

      <div className="card space-y-4">
        <h3 className="text-sm font-semibold text-surface-900">User access</h3>
        <Table<User>
          columns={[
            { header: 'User', cell: (row) => row.username },
            { header: 'Email', cell: (row) => row.email },
            { header: 'Role', cell: (row) => row.role.toUpperCase() },
            { header: 'Status', cell: (row) => (row.is_active ? 'Active' : 'Inactive') },
          ]}
          data={usersQuery.data ?? []}
          emptyMessage="No users found."
        />
      </div>
    </div>
  )
}
