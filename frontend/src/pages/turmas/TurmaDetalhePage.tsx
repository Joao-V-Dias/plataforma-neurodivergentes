import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { UserMinus, UserPlus } from 'lucide-react'
import * as turmasApi from '@/lib/api/turmas'
import * as usuariosApi from '@/lib/api/usuarios'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { SelectField } from '@/components/ui/Select'
import { PageSpinner } from '@/components/ui/Spinner'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'

export function TurmaDetalhePage() {
  const { turmaId } = useParams<{ turmaId: string }>()
  const queryClient = useQueryClient()
  const { notificar } = useToast()
  const [dialogMatricula, setDialogMatricula] = useState(false)
  const [alunoSelecionado, setAlunoSelecionado] = useState('')

  const turmaQuery = useQuery({
    queryKey: ['turma', turmaId],
    queryFn: () => turmasApi.obterTurma(turmaId!),
    enabled: !!turmaId,
  })
  const matriculasQuery = useQuery({
    queryKey: ['matriculas', turmaId],
    queryFn: () => turmasApi.listarMatriculas(turmaId!),
    enabled: !!turmaId,
  })
  const progressoQuery = useQuery({
    queryKey: ['progresso', turmaId],
    queryFn: () => turmasApi.obterProgressoTurma(turmaId!),
    enabled: !!turmaId,
  })
  const usuariosQuery = useQuery({
    queryKey: ['usuarios'],
    queryFn: usuariosApi.listarUsuarios,
    enabled: dialogMatricula,
  })

  const matriculasAtivas = matriculasQuery.data?.filter((m) => m.ativo) ?? []
  const alunosDisponiveis = (usuariosQuery.data ?? []).filter(
    (u) => u.papel === 'aluno' && u.is_active && !matriculasAtivas.some((m) => m.aluno_id === u.id),
  )

  const matricularMutation = useMutation({
    mutationFn: (alunoId: string) => turmasApi.matricularAluno(turmaId!, alunoId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['matriculas', turmaId] })
      void queryClient.invalidateQueries({ queryKey: ['turma', turmaId] })
      notificar({ titulo: 'Aluno matriculado', tone: 'success' })
      setDialogMatricula(false)
      setAlunoSelecionado('')
    },
    onError: (erro) => notificar({ titulo: 'Erro ao matricular', descricao: mensagemDeErro(erro), tone: 'danger' }),
  })

  const desmatricularMutation = useMutation({
    mutationFn: (alunoId: string) => turmasApi.desmatricularAluno(turmaId!, alunoId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['matriculas', turmaId] })
      void queryClient.invalidateQueries({ queryKey: ['turma', turmaId] })
      notificar({ titulo: 'Aluno desmatriculado', tone: 'info' })
    },
    onError: (erro) => notificar({ titulo: 'Erro ao desmatricular', descricao: mensagemDeErro(erro), tone: 'danger' }),
  })

  if (turmaQuery.isLoading) return <PageSpinner label="Carregando turma..." />
  const turma = turmaQuery.data
  if (!turma) return null

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader
          title={turma.nome}
          description={`Período ${turma.periodo} · ${turma.total_professores} professor(es) · ${turma.total_alunos_ativos} aluno(s) ativo(s)`}
        />
      </Card>

      <Card>
        <CardHeader
          title="Alunos matriculados"
          action={
            <Button onClick={() => setDialogMatricula(true)}>
              <UserPlus className="h-4 w-4" aria-hidden="true" />
              Matricular aluno
            </Button>
          }
        />
        {matriculasQuery.isLoading && <PageSpinner label="Carregando matrículas..." />}
        {matriculasAtivas.length === 0 && !matriculasQuery.isLoading && (
          <p className="py-4 text-center text-sm text-[var(--color-muted)]">
            Nenhum aluno matriculado ainda.
          </p>
        )}
        <ul className="flex flex-col gap-2">
          {matriculasAtivas.map((m) => (
            <li
              key={m.id}
              className="flex items-center justify-between rounded-md border border-[var(--color-border)] px-4 py-2.5"
            >
              <div>
                <p className="font-medium text-[var(--color-fg)]">{m.aluno_nome}</p>
                <p className="text-xs text-[var(--color-muted)]">{m.aluno_email}</p>
              </div>
              <Button
                variant="secondary"
                className="px-3 py-1 text-xs"
                carregando={desmatricularMutation.isPending && desmatricularMutation.variables === m.aluno_id}
                onClick={() => desmatricularMutation.mutate(m.aluno_id)}
              >
                <UserMinus className="h-3.5 w-3.5" aria-hidden="true" />
                Remover
              </Button>
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <CardHeader title="Progresso da turma" description="Baseado nas submissões de código (Parte 5)." />
        {progressoQuery.isLoading && <PageSpinner label="Carregando progresso..." />}
        {progressoQuery.data && progressoQuery.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-muted)]">
                  <th scope="col" className="py-2 pr-4 font-medium">Aluno</th>
                  <th scope="col" className="py-2 pr-4 font-medium">Problemas resolvidos</th>
                  <th scope="col" className="py-2 pr-4 font-medium">Tentativas</th>
                  <th scope="col" className="py-2 pr-4 font-medium">Tempo gasto</th>
                </tr>
              </thead>
              <tbody>
                {progressoQuery.data.map((p) => (
                  <tr key={p.aluno_id} className="border-b border-[var(--color-border)] last:border-0">
                    <td className="py-2.5 pr-4">{p.aluno_nome}</td>
                    <td className="py-2.5 pr-4">
                      <Badge tone="success">{p.problemas_resolvidos}</Badge>
                    </td>
                    <td className="py-2.5 pr-4">{p.tentativas}</td>
                    <td className="py-2.5 pr-4">{p.tempo_gasto_minutos} min</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {progressoQuery.data && progressoQuery.data.length === 0 && (
          <p className="py-4 text-center text-sm text-[var(--color-muted)]">Sem dados de progresso ainda.</p>
        )}
      </Card>

      <Dialog open={dialogMatricula} onOpenChange={setDialogMatricula} title="Matricular aluno">
        <div className="flex flex-col gap-4">
          <SelectField
            label="Aluno"
            value={alunoSelecionado}
            onChange={setAlunoSelecionado}
            opcoes={alunosDisponiveis.map((a) => ({ value: a.id, label: `${a.nome} (${a.email})` }))}
            placeholder={alunosDisponiveis.length === 0 ? 'Nenhum aluno disponível' : 'Selecione...'}
            disabled={alunosDisponiveis.length === 0}
          />
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setDialogMatricula(false)}>
              Cancelar
            </Button>
            <Button
              type="button"
              disabled={!alunoSelecionado}
              carregando={matricularMutation.isPending}
              onClick={() => matricularMutation.mutate(alunoSelecionado)}
            >
              Matricular
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}
