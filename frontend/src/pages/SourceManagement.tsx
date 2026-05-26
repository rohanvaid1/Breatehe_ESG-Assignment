import { useQuery } from '@tanstack/react-query'

import Badge from '../components/common/Badge'
import Table from '../components/common/Table'
import api from '../services/apiClient'
import type { SourceSystem } from '../types'
import { unwrapList } from '../utils/api'

export default function SourceManagement() {
  const sourcesQuery = useQuery({
    queryKey: ['sources'],
    queryFn: async (): Promise<SourceSystem[]> => {
      const response = await api.get('/source-systems/')
      return unwrapList<SourceSystem>(response.data)
    },
  })

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-sm font-semibold text-surface-900">Source systems</h3>
        <p className="text-xs text-surface-500">
          Manage ingestion feeds and map each system to its emissions category.
        </p>
      </div>
      <Table<SourceSystem>
        columns={[
          { header: 'Name', cell: (row) => row.name },
          { header: 'Type', cell: (row) => row.source_type.toUpperCase() },
          { header: 'Description', cell: (row) => row.description ?? '--' },
          {
            header: 'Status',
            cell: (row) => (
              <Badge label={row.is_active ? 'Active' : 'Inactive'} variant={row.is_active ? 'success' : 'warning'} />
            ),
          },
        ]}
        data={sourcesQuery.data ?? []}
        emptyMessage="No sources configured."
      />
    </div>
  )
}
