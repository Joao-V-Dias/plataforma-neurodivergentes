import { FileQuestion } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
      <FileQuestion className="h-10 w-10 text-[var(--color-muted)]" aria-hidden="true" />
      <h1 className="text-xl font-semibold text-[var(--color-fg)]">Página não encontrada</h1>
      <p className="max-w-md text-sm text-[var(--color-muted)]">
        O endereço que você acessou não existe ou foi movido.
      </p>
      <ButtonLink to="/" variant="secondary">
        Voltar ao início
      </ButtonLink>
    </div>
  )
}
