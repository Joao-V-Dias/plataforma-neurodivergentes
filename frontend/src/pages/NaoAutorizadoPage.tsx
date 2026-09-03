import { Link } from 'react-router-dom'

export function NaoAutorizadoPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-3)' }}>
      <h1 style={{ fontSize: 'var(--text-h2)' }}>Acesso não autorizado</h1>
      <p style={{ color: 'var(--text-secondary)' }}>Você não tem permissão para ver esta página.</p>
      <Link to="/">Voltar ao início</Link>
    </div>
  )
}
