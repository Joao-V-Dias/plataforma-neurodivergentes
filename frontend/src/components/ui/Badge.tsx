import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import './Badge.css'

type Tom = 'neutro' | 'sucesso' | 'erro' | 'aviso' | 'info' | 'accent'

export function Badge({ tom = 'neutro', children }: { tom?: Tom; children: ReactNode }) {
  return <span className={cn('badge', `badge--${tom}`)}>{children}</span>
}
