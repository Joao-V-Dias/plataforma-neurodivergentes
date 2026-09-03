import './Spinner.css'

export function Spinner({ tamanho = 18 }: { tamanho?: number }) {
  return (
    <span
      className="spinner"
      style={{ width: tamanho, height: tamanho }}
      role="status"
      aria-label="Carregando"
    />
  )
}

export function PageSpinner({ texto = 'Carregando…' }: { texto?: string }) {
  return (
    <div className="page-spinner">
      <Spinner tamanho={26} />
      <span>{texto}</span>
    </div>
  )
}
