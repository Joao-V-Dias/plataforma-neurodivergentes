import type { ReactNode } from 'react'
import { useAuth } from './useAuth'
import { papelAtendeMinimo, type Papel } from '@/lib/api/types'

export function RoleGate({ minimo, children }: { minimo: Papel; children: ReactNode }) {
  const { usuario } = useAuth()
  if (!usuario || !papelAtendeMinimo(usuario.papel, minimo)) return null
  return <>{children}</>
}
