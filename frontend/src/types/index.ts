export type Organization = {
  id: string
  name: string
  slug: string
  industry?: string
  country?: string
  timezone?: string
  is_active: boolean
}

export type User = {
  id: string
  username: string
  email: string
  role: 'admin' | 'analyst' | 'viewer'
  organization?: Organization | null
  is_active: boolean
}

export type SourceSystem = {
  id: string
  name: string
  source_type: 'sap' | 'utility' | 'travel'
  description?: string
  is_active: boolean
}

export type UploadBatch = {
  id: string
  organization: string
  source_system: SourceSystem
  original_filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_rows: number
  success_rows: number
  failed_rows: number
  created_at: string
}

export type AnomalyFlag = {
  id: string
  code: string
  message: string
  severity: 'low' | 'medium' | 'high'
  created_at: string
}

export type NormalizedRecord = {
  id: string
  source_system: SourceSystem
  emission_scope: 'scope_1' | 'scope_2' | 'scope_3'
  activity_quantity: string | null
  activity_unit: string
  normalized_quantity: string | null
  normalized_unit: string
  emission_factor: string | null
  estimated_emissions: string | null
  status: 'pending' | 'approved' | 'rejected'
  is_anomalous: boolean
  data: Record<string, unknown>
  anomalies: AnomalyFlag[]
  created_at: string
}

export type AuditLog = {
  id: string
  record: string
  action: string
  note: string
  performed_by?: User
  created_at: string
}

export type DashboardMetrics = {
  cards: {
    total_uploaded_rows: number
    anomaly_count: number
    approval_pending: number
    approved_rows: number
    rejected_rows: number
  }
  emissions_by_source: Array<{ source_system__source_type: string; emissions: number; count: number }>
  emissions_by_scope: Array<{ emission_scope: string; emissions: number; count: number }>
  monthly_trends: Array<{ month: string; emissions: number }>
}
