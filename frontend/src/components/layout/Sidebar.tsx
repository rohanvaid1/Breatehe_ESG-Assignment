import { NavLink } from 'react-router-dom'

const navItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/upload', label: 'Upload Center' },
  { path: '/sources', label: 'Source Management' },
  { path: '/review', label: 'Analyst Review' },
  { path: '/audit', label: 'Audit Logs' },
  { path: '/organization', label: 'Organization' },
]

export default function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r border-surface-200 bg-white px-6 py-8">
      <div className="mb-10">
        <h1 className="text-lg font-semibold text-surface-900">Breathe ESG</h1>
        <p className="text-xs text-surface-500">Ingestion & Review</p>
      </div>
      <nav className="flex flex-col gap-2 text-sm font-medium">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              [
                'rounded-lg px-3 py-2',
                isActive ? 'bg-brand-50 text-brand-600' : 'text-surface-600 hover:bg-surface-100',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto rounded-2xl border border-surface-200 bg-surface-100 p-4 text-xs text-surface-600">
        <p className="font-semibold text-surface-700">Audit ready</p>
        <p>All approvals are tracked and locked once finalized.</p>
      </div>
    </aside>
  )
}
