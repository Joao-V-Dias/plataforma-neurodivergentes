import type { ReactNode } from 'react'
import './EmptyState.css'

export function EmptyState({
  titulo,
  descricao,
  acao,
}: {
  titulo: string
  descricao?: string
  acao?: ReactNode
}) {
  return (
    <div className="empty-state">
      <p className="empty-state__titulo">{titulo}</p>
      {descricao && <p className="empty-state__descricao">{descricao}</p>}
      {acao && <div className="empty-state__acao">{acao}</div>}
    </div>
  )
}

export function ErrorState({ mensagem, onRetry }: { mensagem: string; onRetry?: () => void }) {
  return (
    <div className="empty-state empty-state--erro" role="alert">
      <p className="empty-state__titulo">Não foi possível carregar</p>
      <p className="empty-state__descricao">{mensagem}</p>
      {onRetry && (
        <button className="empty-state__retry" onClick={onRetry}>
          Tentar novamente
        </button>
      )}
    </div>
  )
}
