import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Table from '../components/common/Table'
import useToast from '../components/common/useToast'
import api from '../services/apiClient'
import type { NormalizedRecord } from '../types'
import { formatNumber, formatScope } from '../utils/format'

type PaginatedResponse = {
  count: number
  next: string | null
  previous: string | null
  results: NormalizedRecord[]
}

export default function ReviewQueue() {
  const { notify } = useToast()
  const [status, setStatus] = useState('pending')
  const [scope, setScope] = useState('')
  const [anomalousOnly, setAnomalousOnly] = useState(false)
  const [page, setPage] = useState(1)

  const recordsQuery = useQuery({
    queryKey: ['normalized-records', status, scope, anomalousOnly, page],
    queryFn: async (): Promise<PaginatedResponse> => {
      const params: Record<string, string> = { page: String(page) }
      if (status) params.status = status
      if (scope) params.emission_scope = scope
      if (anomalousOnly) params.is_anomalous = 'true'
      const response = await api.get('/normalized-records/', { params })
      if (Array.isArray(response.data)) {
        return { count: response.data.length, next: null, previous: null, results: response.data }
      }
      return response.data as PaginatedResponse
    },
  })

  const records = recordsQuery.data?.results ?? []
  const totalCount = recordsQuery.data?.count ?? 0
  const hasNext = Boolean(recordsQuery.data?.next)
  const hasPrev = Boolean(recordsQuery.data?.previous)

  const approveMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/normalized-records/${id}/approve/`, { comment: 'Approved in review queue.' })
    },
    onSuccess: () => {
      notify('Record approved.', 'success')
      recordsQuery.refetch()
    },
    onError: () => notify('Approval failed.', 'error'),
  })

  const rejectMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/normalized-records/${id}/reject/`, { comment: 'Rejected in review queue.' })
    },
    onSuccess: () => {
      notify('Record rejected.', 'success')
      recordsQuery.refetch()
    },
    onError: () => notify('Rejection failed.', 'error'),
  })

  const bulkApproveMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      await api.post('/normalized-records/bulk_approve/', { ids })
    },
    onSuccess: () => {
      notify('Bulk approval completed.', 'success')
      recordsQuery.refetch()
    },
    onError: () => notify('Bulk approval failed.', 'error'),
  })

  const pendingOnPage = records.filter((r) => r.status === 'pending')

  return (
    <div className="space-y-6">
      <div className="card flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-sm font-semibold text-surface-900">Analyst review queue</h3>
          <p className="text-xs text-surface-500">
            Review flagged records, edit normalized values, and approve before audit lock.
            {totalCount > 0 && (
              <span className="ml-2 font-medium text-surface-700">{totalCount} total records</span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-3 text-sm">
          <select
            className="rounded-lg border border-surface-200 px-3 py-2"
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1) }}
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select
            className="rounded-lg border border-surface-200 px-3 py-2"
            value={scope}
            onChange={(e) => { setScope(e.target.value); setPage(1) }}
          >
            <option value="">All scopes</option>
            <option value="scope_1">Scope 1</option>
            <option value="scope_2">Scope 2</option>
            <option value="scope_3">Scope 3</option>
          </select>
          <label className="flex items-center gap-2 text-xs text-surface-600">
            <input
              type="checkbox"
              checked={anomalousOnly}
              onChange={(e) => { setAnomalousOnly(e.target.checked); setPage(1) }}
            />
            Anomalies only
          </label>
          <Button
            variant="secondary"
            onClick={() => bulkApproveMutation.mutate(pendingOnPage.map((r) => r.id))}
            disabled={bulkApproveMutation.isPending || pendingOnPage.length === 0}
          >
            Bulk approve page
          </Button>
        </div>
      </div>

      <Table<NormalizedRecord>
        columns={[
          {
            header: 'Record',
            cell: (row) => (
              <Link to={`/records/${row.id}`} className="font-mono text-xs text-brand-600 hover:underline">
                {row.id.slice(0, 8)}
              </Link>
            ),
          },
          { header: 'Source', cell: (row) => row.source_system?.name ?? '--' },
          { header: 'Scope', cell: (row) => formatScope(row.emission_scope) },
          {
            header: 'Quantity',
            cell: (row) => `${formatNumber(row.normalized_quantity)} ${row.normalized_unit}`,
          },
          {
            header: 'Emissions (kg CO₂e)',
            cell: (row) => formatNumber(row.estimated_emissions),
          },
          {
            header: 'Anomaly',
            cell: (row) =>
              row.is_anomalous ? (
                <Badge label="Flagged" variant="danger" />
              ) : (
                <Badge label="Clear" variant="success" />
              ),
          },
          {
            header: 'Status',
            cell: (row) => (
              <Badge
                label={row.status}
                variant={
                  row.status === 'pending' ? 'warning' : row.status === 'rejected' ? 'danger' : 'success'
                }
              />
            ),
          },
          {
            header: 'Actions',
            cell: (row) => (
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => approveMutation.mutate(row.id)}
                  disabled={approveMutation.isPending || row.status !== 'pending'}
                >
                  Approve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => rejectMutation.mutate(row.id)}
                  disabled={rejectMutation.isPending || row.status !== 'pending'}
                >
                  Reject
                </Button>
              </div>
            ),
          },
        ]}
        data={records}
        emptyMessage={recordsQuery.isLoading ? 'Loading...' : 'No records in this queue.'}
      />

      {(hasPrev || hasNext) && (
        <div className="flex items-center justify-between text-sm text-surface-600">
          <span>Page {page}</span>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setPage((p) => p - 1)} disabled={!hasPrev}>
              ← Previous
            </Button>
            <Button variant="secondary" onClick={() => setPage((p) => p + 1)} disabled={!hasNext}>
              Next →
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
