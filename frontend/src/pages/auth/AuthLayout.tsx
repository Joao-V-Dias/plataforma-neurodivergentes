import type { ReactNode } from 'react'
import './AuthLayout.css'

export function AuthLayout({
  titulo,
  subtitulo,
  children,
  rodape,
}: {
  titulo: string
  subtitulo?: string
  children: ReactNode
  rodape?: ReactNode
}) {
  return (
    <div className="auth-layout">
      <div className="auth-layout__card">
        <div className="auth-layout__marca">
          <span className="auth-layout__logo" aria-hidden="true">
            {'</>'}
          </span>
          <span>Plataforma Adaptativa</span>
        </div>
        <h1 className="auth-layout__titulo">{titulo}</h1>
        {subtitulo && <p className="auth-layout__subtitulo">{subtitulo}</p>}
        <div className="auth-layout__corpo">{children}</div>
        {rodape && <div className="auth-layout__rodape">{rodape}</div>}
      </div>
    </div>
  )
}
