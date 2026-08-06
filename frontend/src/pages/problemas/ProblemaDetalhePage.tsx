import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import * as problemasApi from '@/lib/api/problemas'
import { NIVEL_DIFICULDADE_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { BotaoOuvir } from '@/components/ui/BotaoOuvir'
import { PageSpinner } from '@/components/ui/Spinner'
import { useAuth } from '@/lib/auth/useAuth'
import { SubmissaoPanel } from './SubmissaoPanel'
import { DicasPanel } from './DicasPanel'
import { VincularTurmaCard } from './VincularTurmaCard'
import { SubmissoesDoProblemaCard } from './SubmissoesDoProblemaCard'

const NIVEL_TONE = { facil: 'success', medio: 'warning', dificil: 'danger' } as const

export function ProblemaDetalhePage() {
  const { problemaId } = useParams<{ problemaId: string }>()
  const { usuario } = useAuth()

  const { data: problema, isLoading } = useQuery({
    queryKey: ['problema', problemaId],
    queryFn: () => problemasApi.obterProblema(problemaId!),
    enabled: !!problemaId,
  })

  if (isLoading) return <PageSpinner label="Carregando problema..." />
  if (!problema || !problemaId) return null

  const ehAluno = usuario?.papel === 'aluno'

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader
          title={problema.titulo}
          action={<Badge tone={NIVEL_TONE[problema.nivel_dificuldade]}>{NIVEL_DIFICULDADE_LABEL[problema.nivel_dificuldade]}</Badge>}
        />
        <div className="mb-3 flex flex-wrap gap-1.5">
          {problema.tags.map((tag) => (
            <Badge key={tag.id} tone="neutral">
              {tag.nome}
            </Badge>
          ))}
        </div>
        <p className="mb-3 whitespace-pre-wrap text-sm text-[var(--color-fg)]">{problema.enunciado}</p>
        <BotaoOuvir texto={problema.enunciado} rotulo="o enunciado" />

        {problema.casos.length > 0 && (
          <div className="mt-4 border-t border-[var(--color-border)] pt-4">
            {/* O backend já filtra: um Aluno só recebe casos públicos neste
                array (ver app/api/v1/problemas.py:_problema_detalhe_response);
                Professor+ recebe todos, inclusive ocultos. */}
            <h3 className="mb-2 text-sm font-medium text-[var(--color-fg)]">
              Casos de exemplo{!ehAluno && ' (todos, incluindo ocultos)'}
            </h3>
            <ul className="flex flex-col gap-2">
              {problema.casos.map((caso) => (
                <li
                  key={caso.id}
                  className="flex items-center gap-2 rounded-md border border-[var(--color-border)] p-2.5 font-mono text-xs"
                >
                  <span className="text-[var(--color-muted)]">entrada:</span> {caso.entrada || '(vazia)'}
                  <span className="text-[var(--color-muted)]">·</span>
                  <span className="text-[var(--color-muted)]">saída:</span> {caso.saida_esperada}
                  {!caso.publico && <Badge tone="warning">oculto</Badge>}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      {ehAluno ? (
        <>
          <SubmissaoPanel problemaId={problemaId} />
          <DicasPanel problemaId={problemaId} />
        </>
      ) : (
        <>
          <VincularTurmaCard problemaId={problemaId} />
          <SubmissoesDoProblemaCard problemaId={problemaId} />
        </>
      )}
    </div>
  )
}
