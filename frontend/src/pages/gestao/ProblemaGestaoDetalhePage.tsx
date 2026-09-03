import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ErrorState } from '@/components/ui/EmptyState'
import { Field } from '@/components/ui/Field'
import { PageSpinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Tabs } from '@/components/ui/Tabs'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import { listarSubmissoesDoProblema, obterProblema, vincularProblemaATurma } from '@/lib/api/problemas'
import { listarTurmas } from '@/lib/api/turmas'
import { NIVEL_DIFICULDADE_LABEL, STATUS_SUBMISSAO_LABEL, type StatusSubmissao } from '@/lib/api/types'
import './ProblemaGestaoDetalhePage.css'

const TOM_STATUS: Record<StatusSubmissao, 'sucesso' | 'erro'> = {
  aceito: 'sucesso',
  reprovado: 'erro',
  erro_execucao: 'erro',
  tempo_excedido: 'erro',
  erro_interno: 'erro',
}

export function ProblemaGestaoDetalhePage() {
  const { problemaId } = useParams<{ problemaId: string }>()
  const [aba, setAba] = useState('casos')

  const problemaQuery = useQuery({ queryKey: ['problema', problemaId], queryFn: () => obterProblema(problemaId!) })

  if (problemaQuery.isLoading) return <PageSpinner />
  if (problemaQuery.isError) {
    return <ErrorState mensagem={paraErroApi(problemaQuery.error).message} onRetry={() => problemaQuery.refetch()} />
  }
  const problema = problemaQuery.data!

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>{problema.titulo}</h1>
          <p>
            {NIVEL_DIFICULDADE_LABEL[problema.nivel_dificuldade]} · {problema.linguagem}
          </p>
        </div>
      </header>

      <Tabs
        value={aba}
        onValueChange={setAba}
        abas={[
          {
            value: 'casos',
            label: 'Enunciado e casos',
            conteudo: (
              <div className="problema-gestao__enunciado">
                <p>{problema.enunciado}</p>
                <Table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Entrada</th>
                      <th>Saída esperada</th>
                      <th>Visibilidade</th>
                    </tr>
                  </thead>
                  <tbody>
                    {problema.casos.map((c, i) => (
                      <tr key={c.id}>
                        <td>{i + 1}</td>
                        <td>
                          <code>{c.entrada || '(vazia)'}</code>
                        </td>
                        <td>
                          <code>{c.saida_esperada}</code>
                        </td>
                        <td>
                          <Badge tom={c.publico ? 'info' : 'neutro'}>{c.publico ? 'Público' : 'Oculto'}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            ),
          },
          { value: 'vincular', label: 'Vincular turma', conteudo: <AbaVincular problemaId={problema.id} /> },
          { value: 'submissoes', label: 'Submissões', conteudo: <AbaSubmissoes problemaId={problema.id} /> },
        ]}
      />
    </div>
  )
}

function AbaVincular({ problemaId }: { problemaId: string }) {
  const turmasQuery = useQuery({ queryKey: ['turmas'], queryFn: listarTurmas })
  const [turmaId, setTurmaId] = useState('')
  const [processando, setProcessando] = useState(false)

  async function vincular() {
    if (!turmaId) return
    setProcessando(true)
    try {
      await vincularProblemaATurma(problemaId, turmaId)
      toast({ tipo: 'sucesso', titulo: 'Problema vinculado à turma' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível vincular', descricao: paraErroApi(e).message })
    } finally {
      setProcessando(false)
    }
  }

  return (
    <div className="gestao-form" style={{ maxWidth: '24rem' }}>
      <Field label="Turma" htmlFor="turma-vincular" obrigatorio>
        <Select
          id="turma-vincular"
          value={turmaId}
          onValueChange={setTurmaId}
          opcoes={(turmasQuery.data ?? []).map((t) => ({ value: t.id, label: `${t.nome} (${t.periodo})` }))}
          placeholder="Selecione uma turma"
        />
      </Field>
      <Button carregando={processando} onClick={() => void vincular()}>
        Vincular
      </Button>
    </div>
  )
}

function AbaSubmissoes({ problemaId }: { problemaId: string }) {
  const submissoesQuery = useQuery({
    queryKey: ['submissoes-problema', problemaId],
    queryFn: () => listarSubmissoesDoProblema(problemaId),
  })

  if (submissoesQuery.isLoading) return <PageSpinner />
  if (submissoesQuery.isError) {
    return <ErrorState mensagem={paraErroApi(submissoesQuery.error).message} onRetry={() => submissoesQuery.refetch()} />
  }
  const submissoes = submissoesQuery.data ?? []

  if (submissoes.length === 0) {
    return <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>Nenhuma submissão registrada ainda.</p>
  }

  return (
    <Table>
      <thead>
        <tr>
          <th>Aluno</th>
          <th>Status</th>
          <th>Tempo</th>
          <th>Data</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {submissoes.map((s) => (
          <tr key={s.id}>
            <td className="problema-gestao__id-truncado">{s.aluno_id}</td>
            <td>
              <Badge tom={TOM_STATUS[s.status]}>{STATUS_SUBMISSAO_LABEL[s.status]}</Badge>
            </td>
            <td>{s.tempo_execucao_ms} ms</td>
            <td>{new Date(s.criado_em).toLocaleString('pt-BR')}</td>
            <td>
              <Link to={`/gestao/problemas/${problemaId}/dicas/${s.aluno_id}`}>Ver dicas do aluno</Link>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  )
}
