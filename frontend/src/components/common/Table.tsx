import type { ReactNode } from 'react'

type Column<T> = {
  header: string
  cell: (row: T) => ReactNode
  align?: 'left' | 'right' | 'center'
}

type TableProps<T> = {
  columns: Array<Column<T>>
  data: T[]
  emptyMessage?: string
}

export default function Table<T>({ columns, data, emptyMessage }: TableProps<T>) {
  return (
    <div className="overflow-hidden rounded-2xl border border-surface-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface-100 text-xs uppercase tracking-wide text-surface-500">
          <tr>
            {columns.map((column) => (
              <th
                key={column.header}
                className={[
                  'px-4 py-3',
                  column.align === 'right'
                    ? 'text-right'
                    : column.align === 'center'
                      ? 'text-center'
                      : 'text-left',
                ].join(' ')}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="border-t border-surface-100">
              {columns.map((column) => (
                <td key={column.header} className="px-4 py-3">
                  {column.cell(row)}
                </td>
              ))}
            </tr>
          ))}
          {data.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-center text-surface-500">
                {emptyMessage ?? 'No records found.'}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
