import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

type BadgeTone = 'neutral' | 'success' | 'danger' | 'warning' | 'primary'

// Sem borda no modo normal - só a cor de fundo já basta para diferenciar
// o "pill"; no modo alto contraste (index.css, [data-badge]) a borda
// volta, porque aí as cores de fundo ficam próximas demais do preto.
const toneClasses: Record<BadgeTone, string> = {
  neutral: 'bg-[var(--color-surface)] text-[var(--color-muted)]',
  success: 'bg-[var(--color-success-bg)] text-[var(--color-success)]',
  danger: 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
  warning: 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]',
  primary: 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]',
}

export function Badge({ tone = 'neutral', children }: { tone?: BadgeTone; children: ReactNode }) {
  return (
    <span
      data-badge
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        toneClasses[tone],
      )}
    >
      {children}
    </span>
  )
}
