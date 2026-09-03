import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { ErrorState } from '@/components/ui/EmptyState'
import { Field } from '@/components/ui/Field'
import { PageSpinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Tabs } from '@/components/ui/Tabs'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import {
  adicionarProfessor,
  desmatricularAluno,
  listarMatriculas,
  matricularAluno,
  obterProgressoTurma,
  obterTurma,
} from '@/lib/api/turmas'
import { listarUsuarios } from '@/lib/api/usuarios'
import './TurmaDetalhePage.css'

export function TurmaDetalhePage() {
  const { turmaId } = useParams<{ turmaId: string }>()
  const [aba, setAba] = useState('matriculas')

  const turmaQuery = useQuery({ queryKey: ['turma', turmaId], queryFn: () => obterTurma(turmaId!) })

  if (turmaQuery.isLoading) return <PageSpinner />
  if (turmaQuery.isError) {
    return <ErrorState mensagem={paraErroApi(turmaQuery.error).message} onRetry={() => turmaQuery.refetch()} />
  }
  const turma = turmaQuery.data!

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>{turma.nome}</h1>
          <p>
            {turma.periodo} · {turma.total_professores} professor(es) · {turma.total_alunos_ativos} aluno(s) ativo(s)
          </p>
        </div>
        <Link to={`/gestao/problemas?turma=${turma.id}`}>
          <Button variante="secundario">Ver problemas vinculados</Button>
        </Link>
      </header>

      <Tabs
        value={aba}
        onValueChange={setAba}
        abas={[
          { value: 'matriculas', label: 'Matrículas', conteudo: <AbaMatriculas turmaId={turma.id} /> },
          { value: 'professores', label: 'Professores', conteudo: <AbaProfessores turmaId={turma.id} /> },
          { value: 'progresso', label: 'Progresso', conteudo: <AbaProgresso turmaId={turma.id} /> },
        ]}
      />
    </div>
  )
}

function AbaMatriculas({ turmaId }: { turmaId: string }) {
  const queryClient = useQueryClient()
  const matriculasQuery = useQuery({ queryKey: ['matriculas', turmaId], queryFn: () => listarMatriculas(turmaId) })
  const usuariosQuery = useQuery({ queryKey: ['usuarios'], queryFn: () => listarUsuarios() })
  const alunosDisponiveis = (usuariosQuery.data ?? []).filter(
    (u) => u.papel === 'aluno' && !matriculasQuery.data?.some((m) => m.aluno_id === u.id && m.ativo),
  )

  const [dialogoAberto, setDialogoAberto] = useState(false)
  const [alunoId, setAlunoId] = useState('')
  const [processando, setProcessando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  async function matricular() {
    if (!alunoId) return
    setErro(null)
    setProcessando(true)
    try {
      await matricularAluno(turmaId, alunoId)
      await queryClient.invalidateQueries({ queryKey: ['matriculas', turmaId] })
      setDialogoAberto(false)
      setAlunoId('')
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setProcessando(false)
    }
  }

  async function remover(alunoIdAlvo: string) {
    try {
      await desmatricularAluno(turmaId, alunoIdAlvo)
      await queryClient.invalidateQueries({ queryKey: ['matriculas', turmaId] })
      toast({ tipo: 'info', titulo: 'Aluno removido da turma', descricao: 'O histórico dele foi preservado.' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível remover', descricao: paraErroApi(e).message })
    }
  }

  const ativos = (matriculasQuery.data ?? []).filter((m) => m.ativo)

  return (
    <div>
      <div className="gestao-acao-topo">
        <Dialog
          open={dialogoAberto}
          onOpenChange={setDialogoAberto}
          titulo="Matricular aluno"
          trigger={<Button variante="secundario">Matricular aluno</Button>}
        >
          <div className="gestao-form">
            <Field label="Aluno" htmlFor="aluno-select" obrigatorio>
              <Select
                id="aluno-select"
                value={alunoId}
                onValueChange={setAlunoId}
                opcoes={alunosDisponiveis.map((a) => ({ value: a.id, label: `${a.nome} (${a.email})` }))}
                placeholder="Selecione um aluno"
              />
            </Field>
            {erro && <p className="field__erro" role="alert">{erro}</p>}
            <Button carregando={processando} onClick={() => void matricular()}>
              Matricular
            </Button>
          </div>
        </Dialog>
      </div>
      {matriculasQuery.isLoading && <PageSpinner />}
      {ativos.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>Aluno</th>
              <th>E-mail</th>
              <th>Matriculado em</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {ativos.map((m) => (
              <tr key={m.id}>
                <td>{m.aluno_nome}</td>
                <td>{m.aluno_email}</td>
                <td>{new Date(m.matriculado_em).toLocaleDateString('pt-BR')}</td>
                <td>
                  <button className="gestao-link-perigo" onClick={() => void remover(m.aluno_id)}>
                    Remover da turma
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}

function AbaProfessores({ turmaId }: { turmaId: string }) {
  const usuariosQuery = useQuery({ queryKey: ['usuarios'], queryFn: () => listarUsuarios() })
  const professores = (usuariosQuery.data ?? []).filter((u) => u.papel === 'professor')

  const [dialogoAberto, setDialogoAberto] = useState(false)
  const [professorId, setProfessorId] = useState('')
  const [processando, setProcessando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  async function adicionar() {
    if (!professorId) return
    setErro(null)
    setProcessando(true)
    try {
      await adicionarProfessor(turmaId, professorId)
      setDialogoAberto(false)
      toast({ tipo: 'sucesso', titulo: 'Co-docência adicionada' })
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setProcessando(false)
    }
  }

  return (
    <div className="gestao-acao-topo">
      <Dialog
        open={dialogoAberto}
        onOpenChange={setDialogoAberto}
        titulo="Adicionar professor à turma"
        trigger={<Button variante="secundario">Adicionar professor</Button>}
      >
        <div className="gestao-form">
          <Field label="Professor" htmlFor="professor-select" obrigatorio>
            <Select
              id="professor-select"
              value={professorId}
              onValueChange={setProfessorId}
              opcoes={professores.map((p) => ({ value: p.id, label: p.nome }))}
              placeholder="Selecione um professor"
            />
          </Field>
          {erro && <p className="field__erro" role="alert">{erro}</p>}
          <Button carregando={processando} onClick={() => void adicionar()}>
            Adicionar
          </Button>
        </div>
      </Dialog>
    </div>
  )
}

function AbaProgresso({ turmaId }: { turmaId: string }) {
  const progressoQuery = useQuery({ queryKey: ['progresso-turma', turmaId], queryFn: () => obterProgressoTurma(turmaId) })

  if (progressoQuery.isLoading) return <PageSpinner />
  if (progressoQuery.isError) {
    return <ErrorState mensagem={paraErroApi(progressoQuery.error).message} onRetry={() => progressoQuery.refetch()} />
  }
  const progresso = progressoQuery.data!

  if (progresso.length === 0) {
    return <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>Nenhum dado de progresso ainda.</p>
  }

  return (
    <Table>
      <thead>
        <tr>
          <th>Aluno</th>
          <th>Resolvidos</th>
          <th>Tentativas</th>
          <th>Tempo (min)</th>
        </tr>
      </thead>
      <tbody>
        {progresso.map((p) => (
          <tr key={p.aluno_id}>
            <td>{p.aluno_nome}</td>
            <td>{p.problemas_resolvidos}</td>
            <td>{p.tentativas}</td>
            <td>{p.tempo_gasto_minutos}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  )
}
