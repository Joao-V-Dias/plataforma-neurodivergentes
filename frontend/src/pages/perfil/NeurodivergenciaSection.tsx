import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as perfisApi from '@/lib/api/perfis'
import { useAuth } from '@/lib/auth/useAuth'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { CheckboxField } from '@/components/ui/Checkbox'
import { TextareaField } from '@/components/ui/Input'
import { Alert } from '@/components/ui/Alert'
import { PageSpinner } from '@/components/ui/Spinner'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'

/** Dado sensível de saúde (LGPD Art. 5, II) - a linguagem aqui é
 * deliberadamente cuidadosa: sempre "identificação" e "consentimento",
 * nunca fala em nome do usuário sobre diagnóstico. Espelha
 * app/schemas/perfis.py + docs/lgpd.md. */
export function NeurodivergenciaSection() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const { notificar } = useToast()
  const [editando, setEditando] = useState(false)
  const [condicoesSelecionadas, setCondicoesSelecionadas] = useState<string[]>([])
  const [observacoes, setObservacoes] = useState('')
  const [aceite, setAceite] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  const { data: condicoes, isLoading: carregandoCondicoes } = useQuery({
    queryKey: ['condicoes-neurodivergencia'],
    queryFn: perfisApi.listarCondicoes,
  })

  const { data: perfilVigente, isLoading: carregandoPerfil } = useQuery({
    queryKey: ['perfil-aluno', usuario?.id],
    queryFn: () => perfisApi.obterPerfilAlunoVigente(usuario!.id),
    enabled: !!usuario,
  })

  const mutation = useMutation({
    mutationFn: () =>
      perfisApi.registrarPerfilAluno(usuario!.id, {
        condicoes_codigos: condicoesSelecionadas,
        observacoes: observacoes.trim() || null,
        aceite_consentimento: aceite,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['perfil-aluno', usuario?.id] })
      notificar({ titulo: 'Perfil atualizado', tone: 'success' })
      setEditando(false)
    },
    onError: (e) => setErro(mensagemDeErro(e)),
  })

  function iniciarEdicao() {
    setCondicoesSelecionadas(perfilVigente?.condicoes.map((c) => c.codigo) ?? [])
    setObservacoes(perfilVigente?.observacoes ?? '')
    setAceite(false)
    setErro(null)
    setEditando(true)
  }

  if (carregandoCondicoes || carregandoPerfil) return <PageSpinner label="Carregando perfil..." />

  return (
    <Card>
      <CardHeader
        title="Identificação de neurodivergência"
        description="Usado só para adaptar como o conteúdo e as dicas são apresentados a você - nunca é um diagnóstico e não substitui avaliação profissional."
        action={
          !editando && (
            <Button variant="secondary" onClick={iniciarEdicao}>
              {perfilVigente ? 'Atualizar' : 'Preencher'}
            </Button>
          )
        }
      />

      {!editando && (
        <>
          {perfilVigente ? (
            <div className="flex flex-col gap-3">
              <div className="flex flex-wrap gap-2">
                {perfilVigente.condicoes.length > 0 ? (
                  perfilVigente.condicoes.map((c) => (
                    <Badge key={c.id} tone="primary">
                      {c.nome}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-[var(--color-muted)]">
                    Nenhuma condição identificada nesta versão.
                  </span>
                )}
              </div>
              {perfilVigente.observacoes && (
                <p className="text-sm text-[var(--color-muted)]">{perfilVigente.observacoes}</p>
              )}
              <p className="text-xs text-[var(--color-muted)]">
                Versão {perfilVigente.versao} · registrado em{' '}
                {new Date(perfilVigente.criado_em).toLocaleDateString('pt-BR')}
              </p>
            </div>
          ) : (
            <p className="text-sm text-[var(--color-muted)]">
              Você ainda não preencheu esta informação.
            </p>
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
          <fieldset className="flex flex-col gap-2.5">
            <legend className="mb-1 text-sm font-medium">Condições (selecione quantas se aplicarem)</legend>
            {condicoes?.map((c) => (
              <CheckboxField
                key={c.id}
                label={c.nome}
                descricao={c.descricao ?? undefined}
                checked={condicoesSelecionadas.includes(c.codigo)}
                onChange={(checked) =>
                  setCondicoesSelecionadas((atual) =>
                    checked ? [...atual, c.codigo] : atual.filter((cod) => cod !== c.codigo),
                  )
                }
              />
            ))}
          </fieldset>
          <TextareaField
            label="Observações (opcional)"
            rows={3}
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
          />
          <CheckboxField
            label="Autorizo o tratamento desta informação de saúde para adaptar minha experiência na plataforma."
            checked={aceite}
            onChange={setAceite}
          />
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setEditando(false)}>
              Cancelar
            </Button>
            <Button type="submit" carregando={mutation.isPending} disabled={!aceite}>
              Salvar
            </Button>
          </div>
        </form>
      )}
    </Card>
  )
}
