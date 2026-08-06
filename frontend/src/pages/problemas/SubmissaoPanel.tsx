import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Play } from 'lucide-react'
import * as problemasApi from '@/lib/api/problemas'
import { STATUS_SUBMISSAO_LABEL, type SubmissaoResponse } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Alert } from '@/components/ui/Alert'
import { PageSpinner } from '@/components/ui/Spinner'
import { CodeEditor } from '@/components/code/CodeEditor'
import { ResultadoCasoCard } from '@/components/code/ResultadoCasoCard'
import { mensagemDeErro } from '@/lib/api/errors'

const STATUS_TONE = {
  aceito: 'success',
  reprovado: 'danger',
  erro_execucao: 'danger',
  tempo_excedido: 'warning',
  erro_interno: 'danger',
} as const

const MODELO_INICIAL = '# Escreva sua solução em Python aqui\n'

export function SubmissaoPanel({ problemaId }: { problemaId: string }) {
  const [codigo, setCodigo] = useState(MODELO_INICIAL)
  const [ultimoResultado, setUltimoResultado] = useState<SubmissaoResponse | null>(null)
  const queryClient = useQueryClient()

  const historicoQuery = useQuery({
    queryKey: ['minhas-submissoes', problemaId],
    queryFn: () => problemasApi.listarMinhasSubmissoes(problemaId),
  })

  const mutation = useMutation({
    mutationFn: () => problemasApi.submeterCodigo(problemaId, codigo),
    onSuccess: (resultado) => {
      setUltimoResultado(resultado)
      void queryClient.invalidateQueries({ queryKey: ['minhas-submissoes', problemaId] })
      // A eficácia das dicas (Parte 6) é recalculada no backend quando a
      // submissão é aceita - refletir isso na lista de dicas também.
      void queryClient.invalidateQueries({ queryKey: ['minhas-dicas', problemaId] })
    },
  })

  return (
    <Card>
      <CardHeader title="Sua solução" description="A execução roda isolada, com limite de tempo." />

      <div className="flex flex-col gap-4">
        <CodeEditor value={codigo} onChange={setCodigo} label="Código-fonte (Python)" />

        {mutation.isError && <Alert tone="danger">{mensagemDeErro(mutation.error)}</Alert>}

        <Button
          onClick={() => mutation.mutate()}
          carregando={mutation.isPending}
          disabled={!codigo.trim()}
        >
          <Play className="h-4 w-4" aria-hidden="true" />
          Submeter
        </Button>

        {ultimoResultado && (
          <div className="flex flex-col gap-3 border-t border-[var(--color-border)] pt-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-[var(--color-fg)]">Resultado:</span>
              <Badge tone={STATUS_TONE[ultimoResultado.status]}>
                {STATUS_SUBMISSAO_LABEL[ultimoResultado.status]}
              </Badge>
            </div>
            <div className="flex flex-col gap-2">
              {ultimoResultado.resultados.map((r, i) => (
                <ResultadoCasoCard key={r.caso_teste_id} resultado={r} indice={i} />
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-[var(--color-border)] pt-4">
          <h3 className="mb-2 text-sm font-medium text-[var(--color-fg)]">Histórico de tentativas</h3>
          {historicoQuery.isLoading && <PageSpinner label="Carregando histórico..." />}
          {historicoQuery.data && historicoQuery.data.length === 0 && (
            <p className="text-sm text-[var(--color-muted)]">Você ainda não tentou este problema.</p>
          )}
          {historicoQuery.data && historicoQuery.data.length > 0 && (
            <ul className="flex flex-col gap-1.5">
              {historicoQuery.data.map((s) => (
                <li key={s.id} className="flex items-center justify-between text-sm">
                  <span className="text-[var(--color-muted)]">
                    {new Date(s.criado_em).toLocaleString('pt-BR')}
                  </span>
                  <Badge tone={STATUS_TONE[s.status]}>{STATUS_SUBMISSAO_LABEL[s.status]}</Badge>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Card>
  )
}
