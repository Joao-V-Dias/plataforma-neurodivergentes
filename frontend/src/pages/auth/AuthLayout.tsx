import type { ReactNode } from 'react'
import { Card } from '@/components/ui/Card'

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-surface)] px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-bold text-[var(--color-primary)]">Plataforma Adaptativa</h1>
          <p className="mt-1 text-sm text-[var(--color-muted)]">
            Educação em programação para pessoas neurodivergentes
          </p>
        </div>
        <Card>
          <h2 className="mb-1 text-lg font-semibold text-[var(--color-fg)]">{title}</h2>
          {subtitle && <p className="mb-5 text-sm text-[var(--color-muted)]">{subtitle}</p>}
          {children}
        </Card>
      </div>
    </div>
  )
}
