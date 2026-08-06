import { useAuth } from '@/lib/auth/useAuth'
import { TurmasListPage } from './TurmasListPage'
import { MinhasTurmasPage } from './MinhasTurmasPage'

/** Ponto de entrada de /turmas: o conteúdo depende do papel porque o
 * backend também trata os dois casos de forma completamente diferente
 * (Professor+ usa GET /turmas + gestão; Aluno usa GET /me/turmas,
 * somente leitura do próprio progresso). */
export function TurmasPage() {
  const { usuario } = useAuth()
  if (usuario?.papel === 'aluno') return <MinhasTurmasPage />
  return <TurmasListPage />
}
