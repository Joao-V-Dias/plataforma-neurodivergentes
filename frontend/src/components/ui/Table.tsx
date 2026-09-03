import type { ReactNode } from 'react'
import './Table.css'

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="table__wrap">
      <table className="table">{children}</table>
    </div>
  )
}
