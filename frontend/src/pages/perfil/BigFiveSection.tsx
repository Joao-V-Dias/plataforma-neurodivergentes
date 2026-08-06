import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as perfisApi from '@/lib/api/perfis'
import { useAuth } from '@/lib/auth/useAuth'
import type { BigFiveScores, QuestaoTIPI } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { PageSpinner } from '@/components/ui/Spinner'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'

const TRACO_LABEL: Record<keyof BigFiveScores, string> = {
  abertura: 'Abertura a experiências',
  conscienciosidade: 'Conscienciosidade',
  extroversao: 'Extroversão',
  amabilidade: 'Amabilidade',
  neuroticismo: 'Neuroticismo',
}

function EscalaTIPI({
  questao,
  value,
  onChange,
}: {
  questao: QuestaoTIPI
  value: number | undefined
  onChange: (v: number) => void
}) {
  const name = `tipi-${questao.ordem}`
  return (
    <fieldset className="border-b border-[var(--color-border)] pb-4 last:border-0">
      <legend className="mb-2 text-sm font-medium text-[var(--color-fg)]">{questao.texto}</legend>
      <div className="mb-1 flex justify-between text-xs text-[var(--color-muted)]">
        <span>Discordo totalmente</span>
        <span>Concordo totalmente</span>
      </div>
      <div className="flex justify-between gap-1">
        {[1, 2, 3, 4, 5, 6, 7].map((n) => (
          <label key={n} className="flex flex-1 cursor-pointer flex-col items-center gap-1 text-xs">
            <input
              type="radio"
              name={name}
              value={n}
              checked={value === n}
              onChange={() => onChange(n)}
              className="h-4 w-4"
              required
            />
            {n}
          </label>
        ))}
      </div>
    </fieldset>
  )
}

function BarraTraco({ label, valor }: { label: string; valor: number }) {
  const percentual = ((valor - 1) / 6) * 100
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="font-medium text-[var(--color-fg)]">{label}</span>
        <span className="text-[var(--color-muted)]">{valor.toFixed(1)} / 7.0</span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-[var(--color-surface)]">
        <div
          className="h-2.5 rounded-full bg-[var(--color-primary)]"
          style={{ width: `${percentual}%` }}
        />
      </div>
    </div>
  )
}

export function BigFiveSection() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const { notificar } = useToast()
  const [editando, setEditando] = useState(false)
  const [respostas, setRespostas] = useState<Record<number, number>>({})
  const [erro, setErro] = useState<string | null>(null)

  const { data: questionario, isLoading: carregandoQuestionario } = useQuery({
    queryKey: ['big-five-questionario'],
    queryFn: perfisApi.obterQuestionarioBigFive,
  })

  const { data: perfilVigente, isLoading: carregandoPerfil } = useQuery({
    queryKey: ['big-five', usuario?.id],
    queryFn: () => perfisApi.obterBigFiveVigente(usuario!.id),
    enabled: !!usuario,
  })

  const mutation = useMutation({
    mutationFn: () => {
      const ordenadas = [...(questionario ?? [])].sort((a, b) => a.ordem - b.ordem)
      return perfisApi.responderMeuBigFive({
        respostas: ordenadas.map((q) => respostas[q.ordem]),
      })
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['big-five', usuario?.id] })
      notificar({ titulo: 'Questionário salvo', tone: 'success' })
      setEditando(false)
    },
    onError: (e) => setErro(mensagemDeErro(e)),
  })

  if (carregandoQuestionario || carregandoPerfil) return <PageSpinner label="Carregando..." />

  const todasRespondidas = (questionario ?? []).every((q) => respostas[q.ordem] !== undefined)

  return (
    <Card>
      <CardHeader
        title="Perfil Big Five (TIPI)"
        description="Instrumento científico validado (Gosling, Rentfrow & Swann, 2003) usado para calibrar o tom das dicas da IA - não é um teste de personalidade clínico."
        action={
          !editando && (
            <Button variant="secondary" onClick={() => setEditando(true)}>
              {perfilVigente ? 'Refazer' : 'Responder'}
            </Button>
          )
        }
      />

      {!editando && (
        <>
          {perfilVigente ? (
            <div className="flex flex-col gap-3">
              {(Object.keys(TRACO_LABEL) as (keyof BigFiveScores)[]).map((traco) => (
                <BarraTraco key={traco} label={TRACO_LABEL[traco]} valor={perfilVigente.scores[traco]} />
              ))}
              <p className="mt-1 text-xs text-[var(--color-muted)]">
                Versão {perfilVigente.versao} · respondido em{' '}
                {new Date(perfilVigente.criado_em).toLocaleDateString('pt-BR')}
              </p>
            </div>
          ) : (
            <p className="text-sm text-[var(--color-muted)]">Você ainda não respondeu o questionário.</p>
          )}
        </>
      )}

      {editando && (
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault()
            setErro(null)
            mutation.mutate()
          }}
        >
          {erro && <Alert tone="danger">{erro}</Alert>}
          {questionario?.map((q) => (
            <EscalaTIPI
              key={q.ordem}
              questao={q}
              value={respostas[q.ordem]}
              onChange={(v) => setRespostas((atual) => ({ ...atual, [q.ordem]: v }))}
            />
          ))}
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setEditando(false)}>
              Cancelar
            </Button>
            <Button type="submit" carregando={mutation.isPending} disabled={!todasRespondidas}>
              Salvar respostas
            </Button>
          </div>
        </form>
      )}
    </Card>
  )
}
