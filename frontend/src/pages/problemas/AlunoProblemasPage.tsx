import { useQueries, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import * as turmasApi from '@/lib/api/turmas'
import * as problemasApi from '@/lib/api/problemas'
import { NIVEL_DIFICULDADE_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { PageSpinner } from '@/components/ui/Spinner'

const NIVEL_TONE = { facil: 'success', medio: 'warning', dificil: 'danger' } as const

export function AlunoProblemasPage() {
  const turmasQuery = useQuery({ queryKey: ['minhas-turmas'], queryFn: turmasApi.listarMinhasTurmas })

  const problemasQueries = useQueries({
    queries: (turmasQuery.data ?? []).map((turma) => ({
      queryKey: ['problemas-turma', turma.id],
      queryFn: () => problemasApi.listarProblemasDaTurma(turma.id),
      enabled: !!turmasQuery.data,
    })),
  })

  if (turmasQuery.isLoading) return <PageSpinner label="Carregando problemas..." />

  const turmas = turmasQuery.data ?? []
  if (turmas.length === 0) {
    return (
      <Card>
        <CardHeader title="Problemas" />
        <p className="py-6 text-center text-sm text-[var(--color-muted)]">
          Você precisa estar matriculado em uma turma para ver os problemas.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {turmas.map((turma, i) => {
        const problemas = problemasQueries[i]?.data ?? []
        return (
          <Card key={turma.id}>
            <CardHeader title={turma.nome} description={turma.periodo} />
            {problemasQueries[i]?.isLoading && <PageSpinner label="Carregando..." />}
            {problemas.length === 0 && !problemasQueries[i]?.isLoading && (
              <p className="py-3 text-sm text-[var(--color-muted)]">
                Nenhum problema atribuído a esta turma ainda.
              </p>
            )}
            <ul className="flex flex-col gap-2">
              {problemas.map((p) => (
                <li key={p.id}>
                  <Link
                    to={`/problemas/${p.id}`}
                    className="flex items-center justify-between gap-3 rounded-md border border-[var(--color-border)] px-4 py-3 hover:bg-[var(--color-surface)]"
                  >
                    <span className="font-medium text-[var(--color-fg)]">{p.titulo}</span>
                    <Badge tone={NIVEL_TONE[p.nivel_dificuldade]}>
                      {NIVEL_DIFICULDADE_LABEL[p.nivel_dificuldade]}
                    </Badge>
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        )
      })}
    </div>
  )
}
