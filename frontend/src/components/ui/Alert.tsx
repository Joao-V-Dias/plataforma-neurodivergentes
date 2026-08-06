import type { ReactNode } from 'react'
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { cn } from '@/lib/cn'

type AlertTone = 'danger' | 'success' | 'info'

const toneConfig: Record<AlertTone, { classes: string; Icon: typeof Info }> = {
  danger: {
    classes: 'border-[var(--color-danger)] bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
    Icon: AlertTriangle,
  },
  success: {
    classes: 'border-[var(--color-success)] bg-[var(--color-success-bg)] text-[var(--color-success)]',
    Icon: CheckCircle2,
  },
  info: {
    classes: 'border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]',
    Icon: Info,
  },
}

/** Banner inline (não-flutuante) para mensagens de erro/sucesso ligadas a
 * um formulário ou seção da página - usa `role="alert"` para ser
 * anunciado imediatamente por leitores de tela, diferente do Toast
 * (que é para eventos assíncronos genéricos). */
export function Alert({ tone = 'info', children }: { tone?: AlertTone; children: ReactNode }) {
  const { classes, Icon } = toneConfig[tone]
  return (
    <div role="alert" className={cn('flex items-start gap-2.5 rounded-md border p-3 text-sm', classes)}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </div>
  )
}
