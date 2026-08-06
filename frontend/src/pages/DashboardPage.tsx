import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { BookOpen, School, UserCheck, Users } from 'lucide-react'
import * as turmasApi from '@/lib/api/turmas'
import * as problemasApi from '@/lib/api/problemas'
import * as usuariosApi from '@/lib/api/usuarios'
import { useAuth } from '@/lib/auth/useAuth'
import { ButtonLink } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'

function StatCard({ icon: Icon, label, value, to }: { icon: typeof Users; label: string; value: number | string; to: string }) {
  return (
    <ButtonLink to={to} variant="secondary" className="flex-col items-start gap-1 !justify-start p-4 text-left">
      <Icon className="h-5 w-5 text-[var(--color-primary)]" aria-hidden="true" />
      <span className="text-2xl font-bold text-[var(--color-fg)]">{value}</span>
      <span className="text-sm text-[var(--color-muted)]">{label}</span>
    </ButtonLink>
  )
}

function DashboardAluno() {
  const { data: turmas } = useQuery({ queryKey: ['minhas-turmas'], queryFn: turmasApi.listarMinhasTurmas })
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <StatCard icon={School} label="Minhas turmas" value={turmas?.length ?? '—'} to="/turmas" />
      <StatCard icon={BookOpen} label="Ver problemas" value="→" to="/problemas" />
    </div>
  )
}

function DashboardStaff() {
  const { data: turmas } = useQuery({ queryKey: ['turmas'], queryFn: turmasApi.listarTurmas })
  const { data: problemas } = useQuery({ queryKey: ['problemas'], queryFn: problemasApi.listarProblemas })
  const { data: usuarios } = useQuery({ queryKey: ['usuarios'], queryFn: usuariosApi.listarUsuarios })
  const pendentes = usuarios?.filter((u) => !u.is_active) ?? []

  return (
    <div className="flex flex-col gap-6">
      {pendentes.length > 0 && (
        <Alert tone="info">
          {pendentes.length} usuário(s) aguardando aprovação.{' '}
          <Link to="/usuarios" className="font-medium underline">
            Ver usuários
          </Link>
        </Alert>
      )}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard icon={School} label="Turmas" value={turmas?.length ?? '—'} to="/turmas" />
        <StatCard icon={BookOpen} label="Problemas" value={problemas?.length ?? '—'} to="/problemas" />
        <StatCard icon={UserCheck} label="Usuários" value={usuarios?.length ?? '—'} to="/usuarios" />
      </div>
    </div>
  )
}

export function DashboardPage() {
  const { usuario } = useAuth()
  if (!usuario) return null

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-[var(--color-fg)]">Olá, {usuario.nome.split(' ')[0]}!</h1>
        <p className="text-sm text-[var(--color-muted)]">
          {usuario.papel === 'aluno'
            ? 'Continue de onde parou.'
            : 'Visão geral da sua instituição.'}
        </p>
      </div>
      {usuario.papel === 'aluno' ? <DashboardAluno /> : <DashboardStaff />}
    </div>
  )
}
