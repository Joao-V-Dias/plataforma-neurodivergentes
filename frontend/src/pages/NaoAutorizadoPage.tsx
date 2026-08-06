import { ShieldAlert } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'

export function NaoAutorizadoPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
      <ShieldAlert className="h-10 w-10 text-[var(--color-danger)]" aria-hidden="true" />
      <h1 className="text-xl font-semibold text-[var(--color-fg)]">Acesso não autorizado</h1>
      <p className="max-w-md text-sm text-[var(--color-muted)]">
        Seu papel de acesso não tem permissão para ver esta página.
      </p>
      <ButtonLink to="/" variant="secondary">
        Voltar ao início
      </ButtonLink>
    </div>
  )
}
