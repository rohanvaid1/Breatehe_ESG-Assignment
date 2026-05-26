import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import Badge from '../components/common/Badge'
import Button from '../components/common/Button'
import useToast from '../components/common/useToast'
import api from '../services/apiClient'
import type { NormalizedRecord } from '../types'
import { formatNumber, formatScope } from '../utils/format'

export default function RecordDetail() {
  const { recordId } = useParams()
  const { notify } = useToast()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [editing, setEditing] = useState(false)
  const [editValues, setEditValues] = useState({
    normalized_quantity: '',
    normalized_unit: '',
    emission_factor: '',
    estimated_emissions: '',
  })

  const recordQuery = useQuery({
    queryKey: ['record', recordId],
    queryFn: async () => {
      const response = await api.get<NormalizedRecord>(`/normalized-records/${recordId}/`)
      return response.data
    },
    enabled: Boolean(recordId),
  })

  const approveMutation = useMutation({
    mutationFn: async () => {
      await api.post(`/normalized-records/${recordId}/approve/`, { comment: 'Approved from record detail.' })
    },
    onSuccess: () => {
      notify('Record approved and locked.', 'success')
      queryClient.invalidateQueries({ queryKey: ['record', recordId] })
      queryClient.invalidateQueries({ queryKey: ['normalized-records'] })
    },
    onError: () => notify('Approval failed.', 'error'),
  })

  const rejectMutation = useMutation({
    mutationFn: async () => {
      await api.post(`/normalized-records/${recordId}/reject/`, { comment: 'Rejected from record detail.' })
    },
    onSuccess: () => {
      notify('Record rejected.', 'success')
      queryClient.invalidateQueries({ queryKey: ['record', recordId] })
      queryClient.invalidateQueries({ queryKey: ['normalized-records'] })
    },
    onError: () => notify('Rejection failed.', 'error'),
  })

  const editMutation = useMutation({
    mutationFn: async (values: typeof editValues) => {
      await api.patch(`/normalized-records/${recordId}/`, {
        normalized_quantity: values.normalized_quantity || undefined,
        normalized_unit: values.normalized_unit || undefined,
        emission_factor: values.emission_factor || undefined,
        estimated_emissions: values.estimated_emissions || undefined,
      })
    },
    onSuccess: () => {
      notify('Record updated. Change logged in audit trail.', 'success')
      setEditing(false)
      queryClient.invalidateQueries({ queryKey: ['record', recordId] })
    },
    onError: () => notify('Update failed. Record may be locked.', 'error'),
  })

  const record = recordQuery.data

  if (recordQuery.isLoading) {
    return <div className="card text-sm text-surface-500">Loading record...</div>
  }

  if (!record) {
    return <div className="card text-sm text-surface-500">Record not found.</div>
  }

  const isLocked = Boolean(record.locked_at)

  const startEdit = () => {
    setEditValues({
      normalized_quantity: record.normalized_quantity ?? '',
      normalized_unit: record.normalized_unit ?? '',
      emission_factor: record.emission_factor ?? '',
      estimated_emissions: record.estimated_emissions ?? '',
    })
    setEditing(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="font-mono text-sm font-semibold text-surface-900">Record {record.id}</h3>
          <p className="text-xs text-surface-500">
            {record.source_system?.name} · {formatScope(record.emission_scope)}
            {isLocked && <span className="ml-2 text-amber-600 font-medium">🔒 Locked</span>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            label={record.status}
            variant={record.status === 'pending' ? 'warning' : record.status === 'rejected' ? 'danger' : 'success'}
          />
          {!isLocked && record.status === 'pending' && (
            <>
              <Button variant="secondary" onClick={startEdit} disabled={editing}>
                Edit values
              </Button>
              <Button variant="secondary" onClick={() => approveMutation.mutate()} disabled={approveMutation.isPending}>
                Approve
              </Button>
              <Button variant="ghost" onClick={() => rejectMutation.mutate()} disabled={rejectMutation.isPending}>
                Reject
              </Button>
            </>
          )}
          <Button variant="ghost" onClick={() => navigate(-1)}>
            ← Back
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Normalized values — editable */}
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-surface-900">Normalized values</h4>
            {editing && (
              <span className="text-xs text-amber-600 font-medium">Editing — changes create an audit entry</span>
            )}
          </div>

          {editing ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-surface-500">Quantity</label>
                  <input
                    className="mt-1 w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
                    value={editValues.normalized_quantity}
                    onChange={(e) => setEditValues((v) => ({ ...v, normalized_quantity: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-xs text-surface-500">Unit</label>
                  <input
                    className="mt-1 w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
                    value={editValues.normalized_unit}
                    onChange={(e) => setEditValues((v) => ({ ...v, normalized_unit: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-xs text-surface-500">Emission factor</label>
                  <input
                    className="mt-1 w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
                    value={editValues.emission_factor}
                    onChange={(e) => setEditValues((v) => ({ ...v, emission_factor: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-xs text-surface-500">Estimated emissions (kg CO₂e)</label>
                  <input
                    className="mt-1 w-full rounded-lg border border-surface-200 px-3 py-2 text-sm"
                    value={editValues.estimated_emissions}
                    onChange={(e) => setEditValues((v) => ({ ...v, estimated_emissions: e.target.value }))}
                  />
                </div>
              </div>
              <div className="flex gap-2 pt-1">
                <Button onClick={() => editMutation.mutate(editValues)} disabled={editMutation.isPending}>
                  {editMutation.isPending ? 'Saving...' : 'Save changes'}
                </Button>
                <Button variant="ghost" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <dl className="space-y-2 text-sm text-surface-600">
              <div className="flex justify-between">
                <dt>Quantity</dt>
                <dd className="font-semibold text-surface-900">
                  {formatNumber(record.normalized_quantity)} {record.normalized_unit}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Emission factor</dt>
                <dd className="font-semibold text-surface-900">{formatNumber(record.emission_factor)}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Estimated emissions</dt>
                <dd className="font-semibold text-surface-900">
                  {formatNumber(record.estimated_emissions)} kg CO₂e
                </dd>
              </div>
              <div className="flex justify-between">
                <dt>Activity quantity</dt>
                <dd className="font-semibold text-surface-900">
                  {formatNumber(record.activity_quantity)} {record.activity_unit}
                </dd>
              </div>
            </dl>
          )}
        </div>

        {/* Anomalies */}
        <div className="card space-y-3">
          <h4 className="text-sm font-semibold text-surface-900">
            Anomalies
            {record.anomalies.length > 0 && (
              <span className="ml-2 rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700">
                {record.anomalies.length}
              </span>
            )}
          </h4>
          {record.anomalies.length === 0 ? (
            <p className="text-sm text-surface-500">No anomalies detected.</p>
          ) : (
            <ul className="space-y-2 text-sm text-surface-600">
              {record.anomalies.map((anomaly) => (
                <li key={anomaly.id} className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-mono text-xs text-surface-400">[{anomaly.code}]</span>{' '}
                    <span>{anomaly.message}</span>
                  </div>
                  <Badge
                    label={anomaly.severity}
                    variant={anomaly.severity === 'high' ? 'danger' : anomaly.severity === 'medium' ? 'warning' : 'neutral'}
                  />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Raw payload */}
      <div className="card">
        <h4 className="text-sm font-semibold text-surface-900">Raw payload</h4>
        <p className="mt-1 text-xs text-surface-500">
          Original normalized data fields extracted from the source CSV row.
        </p>
        <pre className="mt-3 whitespace-pre-wrap rounded-lg bg-surface-100 p-4 text-xs text-surface-700">
          {JSON.stringify(record.data, null, 2)}
        </pre>
      </div>
    </div>
  )
}
