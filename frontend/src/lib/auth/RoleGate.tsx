import type { ReactNode } from 'react'
import { useAuth } from './useAuth'
import { papelAtendeMinimo, type Papel } from '@/lib/api/types'

interface RoleGateProps {
  children: ReactNode
  /** Papel mínimo exigido para renderizar `children`. */
  papelMinimo?: Papel
  /** Lista explícita de papéis permitidos, quando "mínimo hierárquico"
   * não se aplica (ex: uma ação só de Aluno). */
  papeis?: Papel[]
  fallback?: ReactNode
}

/** Esconde/mostra um trecho de UI conforme o papel do usuário logado -
 * complementa (nunca substitui) a checagem de autorização real, que
 * sempre acontece no backend (app/api/deps.py). Isto é só para não
 * oferecer, na interface, uma ação que o servidor vai recusar de
 * qualquer forma. */
export function RoleGate({ children, papelMinimo, papeis, fallback = null }: RoleGateProps) {
  const { usuario } = useAuth()
  if (!usuario) return <>{fallback}</>

  if (papelMinimo && !papelAtendeMinimo(usuario.papel, papelMinimo)) return <>{fallback}</>
  if (papeis && !papeis.includes(usuario.papel)) return <>{fallback}</>

  return <>{children}</>
}
