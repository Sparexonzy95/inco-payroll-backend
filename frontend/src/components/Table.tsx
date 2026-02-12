import { ReactNode } from 'react'

interface TableProps {
  headers: string[]
  children: ReactNode
}

const Table = ({ headers, children }: TableProps) => {
  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  )
}

export default Table
