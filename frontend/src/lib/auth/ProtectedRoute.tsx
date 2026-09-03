import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { PageSpinner } from '@/components/ui/Spinner'
import { useAuth } from './useAuth'
import type { Papel } from '@/lib/api/types'
import { papelAtendeMinimo } from '@/lib/api/types'

export function ProtectedRoute({
  children,
  papelMinimo,
}: {
  children: ReactNode
  papelMinimo?: Papel
}) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()

  if (carregando) return <PageSpinner />

  if (!usuario) {
    return <Navigate to="/login" state={{ de: location.pathname }} replace />
  }

  if (!usuario.is_active) {
    return <Navigate to="/aguardando-aprovacao" replace />
  }

  if (papelMinimo && !papelAtendeMinimo(usuario.papel, papelMinimo)) {
    return <Navigate to="/nao-autorizado" replace />
  }

  return <>{children}</>
}
