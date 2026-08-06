import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth'
import { papelAtendeMinimo, type Papel } from '@/lib/api/types'
import { PageSpinner } from '@/components/ui/Spinner'

interface ProtectedRouteProps {
  children: ReactNode
  /** Papel mínimo exigido na hierarquia (Diretor > Coordenador > Professor
   * > Aluno) - espelha app/api/deps.py:require_min_role. Omitido = só
   * exige estar autenticado, qualquer papel serve. */
  papelMinimo?: Papel
}

/** Bloqueia acesso a rotas que exigem autenticação (e, opcionalmente, um
 * papel mínimo). Nunca esconde só visualmente - sempre redireciona, para
 * que a barra de endereço nunca mostre uma URL "logada" sem sessão
 * válida. */
export function ProtectedRoute({ children, papelMinimo }: ProtectedRouteProps) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()

  if (carregando) {
    return <PageSpinner label="Carregando sua sessão..." />
  }

  if (!usuario) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (papelMinimo && !papelAtendeMinimo(usuario.papel, papelMinimo)) {
    return <Navigate to="/nao-autorizado" replace />
  }

  return <>{children}</>
}
