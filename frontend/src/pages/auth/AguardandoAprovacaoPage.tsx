import { AuthLayout } from './AuthLayout'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/lib/auth/useAuth'

export function AguardandoAprovacaoPage() {
  const { sair } = useAuth()
  return (
    <AuthLayout titulo="Conta aguardando aprovação">
      <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>
        Sua conta ainda não foi aprovada por um professor da sua instituição. Tente novamente mais
        tarde ou entre em contato com sua turma.
      </p>
      <Button variante="secundario" onClick={() => void sair()}>
        Sair
      </Button>
    </AuthLayout>
  )
}
