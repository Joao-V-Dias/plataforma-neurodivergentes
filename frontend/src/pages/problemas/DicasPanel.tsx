import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Lightbulb, Sparkles } from 'lucide-react'
import * as dicasApi from '@/lib/api/dicas'
import { NIVEL_DICA_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Alert } from '@/components/ui/Alert'
import { BotaoOuvir } from '@/components/ui/BotaoOuvir'
import { PageSpinner } from '@/components/ui/Spinner'
import { mensagemDeErro } from '@/lib/api/errors'

const NIVEL_MAXIMO = 4

/** Motor de dicas progressivas (Parte 6): o aluno só pode pedir a
 * "próxima" dica - o nível é sempre calculado pelo servidor a partir do
 * que já foi dado (ver app/services/dica_service.py), então esta UI nunca
 * oferece escolher um nível diretamente. */
export function DicasPanel({ problemaId }: { problemaId: string }) {
  const queryClient = useQueryClient()

  const { data: dicas, isLoading } = useQuery({
    queryKey: ['minhas-dicas', problemaId],
    queryFn: () => dicasApi.listarMinhasDicas(problemaId),
  })

  const mutation = useMutation({
    mutationFn: () => dicasApi.solicitarDica(problemaId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['minhas-dicas', problemaId] })
    },
  })

  const nivelMaximoRecebido = dicas?.reduce((max, d) => Math.max(max, d.nivel), 0) ?? 0
  const atingiuLimite = nivelMaximoRecebido >= NIVEL_MAXIMO

  return (
    <Card>
      <CardHeader
        title="Dicas"
        description="Cada dica é uma etapa: pergunta, conceito, roteiro e, por fim, uma solução comentada."
      />

      {isLoading && <PageSpinner label="Carregando dicas..." />}

      {dicas && dicas.length === 0 && (
        <p className="mb-4 text-sm text-[var(--color-muted)]">
          Ainda sem dicas para este problema. Tente resolver sozinho primeiro - se travar, peça uma dica.
        </p>
      )}

      {dicas && dicas.length > 0 && (
        <ol className="mb-4 flex flex-col gap-3">
          {[...dicas]
            .sort((a, b) => a.nivel - b.nivel)
            .map((dica) => (
              <li key={dica.id} className="rounded-md border border-[var(--color-border)] p-3">
                <div className="mb-1.5 flex items-center justify-between gap-2">
                  <Badge tone="primary">
                    Nível {dica.nivel} · {NIVEL_DICA_LABEL[dica.nivel]}
                  </Badge>
                  <BotaoOuvir texto={dica.conteudo} rotulo="esta dica" />
                </div>
                <p className="whitespace-pre-wrap text-sm text-[var(--color-fg)]">{dica.conteudo}</p>
              </li>
            ))}
        </ol>
      )}

      {mutation.isError && <Alert tone="danger">{mensagemDeErro(mutation.error)}</Alert>}

      {atingiuLimite ? (
        <p className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          Você já recebeu a dica de nível mais alto para este problema.
        </p>
      ) : (
        <Button variant="secondary" carregando={mutation.isPending} onClick={() => mutation.mutate()}>
          <Lightbulb className="h-4 w-4" aria-hidden="true" />
          Pedir dica
        </Button>
      )}
    </Card>
  )
}
