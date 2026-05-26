import { useQuery } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import StatCard from '../components/common/StatCard'
import api from '../services/apiClient'
import type { DashboardMetrics } from '../types'
import { formatNumber } from '../utils/format'

const COLORS = ['#2b6bff', '#4f8cff', '#86b5ff']

export default function Dashboard() {
  const { data } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await api.get<DashboardMetrics>('/dashboard/metrics/')
      return response.data
    },
  })

  const cards = data?.cards

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total rows" value={formatNumber(cards?.total_uploaded_rows ?? 0, 0)} />
        <StatCard label="Anomalies flagged" value={formatNumber(cards?.anomaly_count ?? 0, 0)} />
        <StatCard label="Approval pending" value={formatNumber(cards?.approval_pending ?? 0, 0)} />
        <StatCard label="Approved rows" value={formatNumber(cards?.approved_rows ?? 0, 0)} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="text-sm font-semibold text-surface-900">Emissions by source</h3>
          <p className="text-xs text-surface-500">Scope totals across SAP, utility, and travel feeds.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.emissions_by_source ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="source_system__source_type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="emissions" fill="#2b6bff" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-surface-900">Emissions by scope</h3>
          <p className="text-xs text-surface-500">Scope 1/2/3 distribution for the period.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.emissions_by_scope ?? []}
                  dataKey="emissions"
                  nameKey="emission_scope"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={6}
                >
                  {(data?.emissions_by_scope ?? []).map((_entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-sm font-semibold text-surface-900">Monthly emissions trend</h3>
        <p className="text-xs text-surface-500">Rolling emissions totals based on ingestion dates.</p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data?.monthly_trends ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="emissions" stroke="#2b6bff" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
