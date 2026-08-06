import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as turmasApi from '@/lib/api/turmas'
import * as problemasApi from '@/lib/api/problemas'
import { Card, CardHeader } from '@/components/ui/Card'
import { SelectField } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'

export function VincularTurmaCard({ problemaId }: { problemaId: string }) {
  const { notificar } = useToast()
  const queryClient = useQueryClient()
  const [turmaSelecionada, setTurmaSelecionada] = useState('')

  const { data: turmas } = useQuery({ queryKey: ['turmas'], queryFn: turmasApi.listarTurmas })

  const mutation = useMutation({
    mutationFn: () => problemasApi.vincularProblemaATurma(problemaId, turmaSelecionada),
    onSuccess: () => {
      notificar({ titulo: 'Problema vinculado à turma', tone: 'success' })
      void queryClient.invalidateQueries({ queryKey: ['problemas-turma', turmaSelecionada] })
      setTurmaSelecionada('')
    },
    onError: (erro) => notificar({ titulo: 'Erro ao vincular', descricao: mensagemDeErro(erro), tone: 'danger' }),
  })

  return (
    <Card>
      <CardHeader title="Vincular a uma turma" description="Só alunos de turmas vinculadas veem este problema." />
      <div className="flex items-end gap-3">
        <div className="flex-1">
          <SelectField
            label="Turma"
            value={turmaSelecionada}
            onChange={setTurmaSelecionada}
            opcoes={(turmas ?? []).map((t) => ({ value: t.id, label: `${t.nome} (${t.periodo})` }))}
            placeholder="Selecione..."
          />
        </div>
        <Button disabled={!turmaSelecionada} carregando={mutation.isPending} onClick={() => mutation.mutate()}>
          Vincular
        </Button>
      </div>
    </Card>
  )
}
