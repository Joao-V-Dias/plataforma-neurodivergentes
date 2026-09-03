import type { ReactNode } from 'react'
import './Field.css'

export function Field({
  label,
  htmlFor,
  erro,
  dica,
  children,
  obrigatorio,
}: {
  label: string
  htmlFor: string
  erro?: string
  dica?: string
  children: ReactNode
  obrigatorio?: boolean
}) {
  return (
    <div className="field">
      <label className="field__label" htmlFor={htmlFor}>
        {label}
        {obrigatorio && <span aria-hidden="true"> *</span>}
      </label>
      {children}
      {dica && !erro && (
        <p className="field__dica" id={`${htmlFor}-dica`}>
          {dica}
        </p>
      )}
      {erro && (
        <p className="field__erro" id={`${htmlFor}-erro`} role="alert">
          {erro}
        </p>
      )}
    </div>
  )
}
