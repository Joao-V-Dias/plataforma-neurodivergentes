import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Lightbulb } from 'lucide-react'
import * as problemasApi from '@/lib/api/problemas'
import * as dicasApi from '@/lib/api/dicas'
import { NIVEL_DICA_LABEL, STATUS_SUBMISSAO_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { PageSpinner } from '@/components/ui/Spinner'

const STATUS_TONE = {
  aceito: 'success',
  reprovado: 'danger',
  erro_execucao: 'danger',
  tempo_excedido: 'warning',
  erro_interno: 'danger',
} as const

export function SubmissoesDoProblemaCard({ problemaId }: { problemaId: string }) {
  const [alunoParaVerDicas, setAlunoParaVerDicas] = useState<string | null>(null)

  const { data: submissoes, isLoading } = useQuery({
    queryKey: ['submissoes-problema', problemaId],
    queryFn: () => problemasApi.listarSubmissoesDoProblema(problemaId),
  })

  // Um aluno pode aparecer em várias submissões; mostramos "ver dicas"
  // uma vez por aluno distinto.
  const alunosUnicos = [...new Set((submissoes ?? []).map((s) => s.aluno_id))]

  return (
    <Card>
      <CardHeader title="Submissões" description="Todas as tentativas de alunos para este problema." />
      {isLoading && <PageSpinner label="Carregando submissões..." />}
      {submissoes && submissoes.length === 0 && (
        <p className="py-4 text-center text-sm text-[var(--color-muted)]">Nenhuma submissão ainda.</p>
      )}
      {submissoes && submissoes.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-[var(--color-muted)]">
                <th scope="col" className="py-2 pr-4 font-medium">Aluno</th>
                <th scope="col" className="py-2 pr-4 font-medium">Status</th>
                <th scope="col" className="py-2 pr-4 font-medium">Quando</th>
                <th scope="col" className="py-2 pr-4 font-medium">
                  <span className="sr-only">Ações</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {submissoes.map((s) => (
                <tr key={s.id} className="border-b border-[var(--color-border)] last:border-0">
                  <td className="py-2.5 pr-4 font-mono text-xs text-[var(--color-muted)]">{s.aluno_id}</td>
                  <td className="py-2.5 pr-4">
                    <Badge tone={STATUS_TONE[s.status]}>{STATUS_SUBMISSAO_LABEL[s.status]}</Badge>
                  </td>
                  <td className="py-2.5 pr-4 text-[var(--color-muted)]">
                    {new Date(s.criado_em).toLocaleString('pt-BR')}
                  </td>
                  <td className="py-2.5 pr-4">
                    {alunosUnicos.includes(s.aluno_id) && (
                      <Button
                        variant="secondary"
                        className="px-3 py-1 text-xs"
                        onClick={() => setAlunoParaVerDicas(s.aluno_id)}
                      >
                        <Lightbulb className="h-3.5 w-3.5" aria-hidden="true" />
                        Ver dicas
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {alunoParaVerDicas && (
        <DicasDeAlunoDialog
          problemaId={problemaId}
          alunoId={alunoParaVerDicas}
          onOpenChange={(open) => !open && setAlunoParaVerDicas(null)}
        />
      )}
    </Card>
  )
}

function DicasDeAlunoDialog({
  problemaId,
  alunoId,
  onOpenChange,
}: {
  problemaId: string
  alunoId: string
  onOpenChange: (open: boolean) => void
}) {
  const { data: dicas, isLoading } = useQuery({
    queryKey: ['dicas-de-aluno', problemaId, alunoId],
    queryFn: () => dicasApi.listarDicasDeAluno(problemaId, alunoId),
  })

  return (
    <Dialog
      open
      onOpenChange={onOpenChange}
      title="Histórico de dicas"
      description="Inclui a eficácia registrada (resolveu depois? em quanto tempo?)."
    >
      {isLoading && <PageSpinner label="Carregando dicas..." />}
      {dicas && dicas.length === 0 && (
        <p className="text-sm text-[var(--color-muted)]">Este aluno ainda não pediu dicas.</p>
      )}
      <ul className="flex max-h-96 flex-col gap-3 overflow-y-auto">
        {[...(dicas ?? [])]
          .sort((a, b) => a.nivel - b.nivel)
          .map((dica) => (
            <li key={dica.id} className="rounded-md border border-[var(--color-border)] p-3">
              <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
                <Badge tone="primary">
                  Nível {dica.nivel} · {NIVEL_DICA_LABEL[dica.nivel]}
                </Badge>
                {dica.adaptacoes_aplicadas.map((codigo) => (
                  <Badge key={codigo} tone="neutral">
                    {codigo}
                  </Badge>
                ))}
                {dica.resolvida_apos && (
                  <Badge tone="success">
                    Resolveu em {Math.round((dica.tempo_ate_resolver_ms ?? 0) / 60000)} min
                  </Badge>
                )}
              </div>
              <p className="whitespace-pre-wrap text-sm text-[var(--color-fg)]">{dica.conteudo}</p>
            </li>
          ))}
      </ul>
    </Dialog>
  )
}
