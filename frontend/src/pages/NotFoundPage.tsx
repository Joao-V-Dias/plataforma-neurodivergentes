import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-3)' }}>
      <h1 style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-h1)' }}>404</h1>
      <p style={{ color: 'var(--text-secondary)' }}>Não encontramos o que você procura.</p>
      <Link to="/">Voltar ao início</Link>
    </div>
  )
}
