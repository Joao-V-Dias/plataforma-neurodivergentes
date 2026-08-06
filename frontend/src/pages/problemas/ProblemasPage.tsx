import { useAuth } from '@/lib/auth/useAuth'
import { ProblemasListPage } from './ProblemasListPage'
import { AlunoProblemasPage } from './AlunoProblemasPage'

export function ProblemasPage() {
  const { usuario } = useAuth()
  if (usuario?.papel === 'aluno') return <AlunoProblemasPage />
  return <ProblemasListPage />
}
