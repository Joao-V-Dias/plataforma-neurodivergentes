import { useQueries, useQuery } from '@tanstack/react-query'
import * as turmasApi from '@/lib/api/turmas'
import { Card, CardHeader } from '@/components/ui/Card'
import { PageSpinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'

export function MinhasTurmasPage() {
  const turmasQuery = useQuery({ queryKey: ['minhas-turmas'], queryFn: turmasApi.listarMinhasTurmas })

  const progressoQueries = useQueries({
    queries: (turmasQuery.data ?? []).map((turma) => ({
      queryKey: ['meu-progresso', turma.id],
      queryFn: () => turmasApi.obterMeuProgresso(turma.id),
      enabled: !!turmasQuery.data,
    })),
  })

  if (turmasQuery.isLoading) return <PageSpinner label="Carregando suas turmas..." />

  const turmas = turmasQuery.data ?? []

  if (turmas.length === 0) {
    return (
      <Card>
        <CardHeader title="Minhas turmas" />
        <p className="py-6 text-center text-sm text-[var(--color-muted)]">
          Você ainda não está matriculado em nenhuma turma.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-[var(--color-fg)]">Minhas turmas</h1>
      <div className="grid gap-4 sm:grid-cols-2">
        {turmas.map((turma, i) => {
          const progresso = progressoQueries[i]?.data
          return (
            <Card key={turma.id}>
              <h2 className="font-semibold text-[var(--color-fg)]">{turma.nome}</h2>
              <p className="mb-3 text-sm text-[var(--color-muted)]">{turma.periodo}</p>
              {progressoQueries[i]?.isLoading && <PageSpinner label="Carregando progresso..." />}
              {progresso && (
                <dl className="flex flex-wrap gap-2">
                  <Badge tone="success">{progresso.problemas_resolvidos} resolvidos</Badge>
                  <Badge tone="neutral">{progresso.tentativas} tentativas</Badge>
                  <Badge tone="neutral">{progresso.tempo_gasto_minutos} min</Badge>
                </dl>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
