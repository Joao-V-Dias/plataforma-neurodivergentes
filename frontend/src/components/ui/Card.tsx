import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/cn'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-card
      className={cn(
        // Sem borda: o contraste sutil entre o branco do cartão e o
        // cinza claro da página (ver body em index.css) já separa os
        // dois; uma sombra bem discreta reforça o "flutuar" sem pesar.
        // (index.css reativa a borda no modo alto contraste via [data-card].)
        'rounded-2xl bg-[var(--color-bg)] p-6 shadow-[0_1px_2px_rgba(20,20,40,0.06)]',
        className,
      )}
      {...props}
    />
  )
}

export function CardHeader({
  title,
  description,
  action,
}: {
  title: ReactNode
  description?: ReactNode
  action?: ReactNode
}) {
  return (
    <div className="mb-5 flex items-start justify-between gap-4">
      <div>
        <h2 className="text-base font-semibold text-[var(--color-fg)]">{title}</h2>
        {description && <p className="mt-1 text-sm text-[var(--color-muted)]">{description}</p>}
      </div>
      {action}
    </div>
  )
}
