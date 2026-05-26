import { useQuery } from '@tanstack/react-query'

import Table from '../components/common/Table'
import api from '../services/apiClient'
import type { AuditLog } from '../types'
import { unwrapList } from '../utils/api'
import { formatDate } from '../utils/format'

export default function AuditLogs() {
  const logsQuery = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async (): Promise<AuditLog[]> => {
      const response = await api.get('/audit-logs/')
      return unwrapList<AuditLog>(response.data)
    },
  })

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-sm font-semibold text-surface-900">Audit trail</h3>
        <p className="text-xs text-surface-500">Immutable log of uploads, edits, approvals, and locks.</p>
      </div>
      <Table<AuditLog>
        columns={[
          { header: 'Action', cell: (row) => row.action.toUpperCase() },
          { header: 'Record', cell: (row) => row.record.slice(0, 8) },
          { header: 'User', cell: (row) => row.performed_by?.username ?? 'System' },
          { header: 'Note', cell: (row) => row.note ?? '--' },
          { header: 'Timestamp', cell: (row) => formatDate(row.created_at) },
        ]}
        data={logsQuery.data ?? []}
        emptyMessage="No audit events yet."
      />
    </div>
  )
}
