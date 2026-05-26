import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { ToastProvider } from './components/common/ToastProvider'
import AppShell from './components/layout/AppShell'
import RequireAuth from './components/layout/RequireAuth'
import AuditLogs from './pages/AuditLogs'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import OrganizationSettings from './pages/OrganizationSettings'
import RecordDetail from './pages/RecordDetail'
import ReviewQueue from './pages/ReviewQueue'
import SourceManagement from './pages/SourceManagement'
import UploadCenter from './pages/UploadCenter'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60_000, refetchOnWindowFocus: false },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth />}>
              <Route element={<AppShell />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/upload" element={<UploadCenter />} />
                <Route path="/sources" element={<SourceManagement />} />
                <Route path="/review" element={<ReviewQueue />} />
                <Route path="/audit" element={<AuditLogs />} />
                <Route path="/records/:recordId" element={<RecordDetail />} />
                <Route path="/organization" element={<OrganizationSettings />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  )
}

export default App
