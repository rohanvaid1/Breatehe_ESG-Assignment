import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import Table from '../components/common/Table'
import useToast from '../components/common/useToast'
import api from '../services/apiClient'
import type { SourceSystem, UploadBatch } from '../types'
import { unwrapList } from '../utils/api'
import { formatDate } from '../utils/format'

export default function UploadCenter() {
  const { notify } = useToast()
  const [selectedSource, setSelectedSource] = useState<string>('')
  const [file, setFile] = useState<File | null>(null)

  const sourcesQuery = useQuery({
    queryKey: ['sources'],
    queryFn: async (): Promise<SourceSystem[]> => {
      const response = await api.get('/source-systems/')
      return unwrapList<SourceSystem>(response.data)
    },
  })

  const batchesQuery = useQuery({
    queryKey: ['upload-batches'],
    queryFn: async (): Promise<UploadBatch[]> => {
      const response = await api.get('/upload-batches/')
      return unwrapList<UploadBatch>(response.data)
    },
  })

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file || !selectedSource) {
        throw new Error('Missing file or source.')
      }
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source_system', selectedSource)
      await api.post('/upload-batches/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    onSuccess: () => {
      notify('Upload queued. Ingestion is running.', 'success')
      setFile(null)
      batchesQuery.refetch()
    },
    onError: () => notify('Upload failed. Check file format.', 'error'),
  })

  return (
    <div className="space-y-6">
      <div className="card space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-surface-900">Upload data feed</h3>
          <p className="text-xs text-surface-500">CSV uploads are parsed and normalized asynchronously.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-[1fr_2fr_auto]">
          <select
            className="rounded-lg border border-surface-200 px-3 py-2 text-sm"
            value={selectedSource}
            onChange={(event) => setSelectedSource(event.target.value)}
          >
            <option value="">Select source system</option>
            {(sourcesQuery.data ?? []).map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
          </select>
          <input
            className="rounded-lg border border-surface-200 px-3 py-2 text-sm"
            type="file"
            accept=".csv"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <Button onClick={() => uploadMutation.mutate()} disabled={uploadMutation.isPending}>
            {uploadMutation.isPending ? 'Uploading...' : 'Queue upload'}
          </Button>
        </div>
      </div>

      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-surface-900">Recent uploads</h3>
            <p className="text-xs text-surface-500">
              Track ingestion progress and review failures. Refresh to see updated status.
            </p>
          </div>
          <Button variant="ghost" onClick={() => batchesQuery.refetch()}>
            Refresh
          </Button>
        </div>
        {(batchesQuery.data ?? []).some((b) => b.status === 'pending' || b.status === 'processing') && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
            Some batches are still processing. If status stays "pending" for more than a few seconds, Redis/Celery
            may not be running — the server will process synchronously on the next request.
          </div>
        )}
        <Table<UploadBatch>
          columns={[
            { header: 'File', cell: (row) => row.original_filename },
            { header: 'Source', cell: (row) => row.source_system?.name ?? '--' },
            { header: 'Status', cell: (row) => <Badge label={row.status} variant={statusToBadge(row.status)} /> },
            {
              header: 'Rows (ok/total)',
              cell: (row) => (
                <span>
                  <span className="text-green-700">{row.success_rows}</span>
                  {row.failed_rows > 0 && (
                    <span className="text-red-600"> / {row.failed_rows} failed</span>
                  )}
                  {' / '}{row.total_rows}
                </span>
              ),
            },
            { header: 'Uploaded', cell: (row) => formatDate(row.created_at) },
          ]}
          data={batchesQuery.data ?? []}
          emptyMessage="No uploads yet."
        />
      </div>
    </div>
  )
}

const statusToBadge = (status: UploadBatch['status']) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'processing':
      return 'info'
    default:
      return 'warning'
  }
}
