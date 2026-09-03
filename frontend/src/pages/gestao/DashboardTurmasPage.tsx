import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { ErrorState } from '@/components/ui/EmptyState'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { PageSpinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import { criarTurma, listarTurmas } from '@/lib/api/turmas'
import { listarUsuarios } from '@/lib/api/usuarios'
import { useAuth } from '@/lib/auth/useAuth'
import './DashboardTurmasPage.css'

export function DashboardTurmasPage() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const turmasQuery = useQuery({ queryKey: ['turmas'], queryFn: listarTurmas })
  const professoresQuery = useQuery({
    queryKey: ['usuarios', 'professor'],
    queryFn: () => listarUsuarios(),
    enabled: usuario?.papel !== 'professor',
  })

  const [dialogoAberto, setDialogoAberto] = useState(false)
  const [nome, setNome] = useState('')
  const [periodo, setPeriodo] = useState('')
  const [professorId, setProfessorId] = useState('')
  const [criando, setCriando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  const professores = (professoresQuery.data ?? []).filter((u) => u.papel === 'professor')

  async function handleCriar() {
    if (!usuario) return
    const responsavelId = usuario.papel === 'professor' ? usuario.id : professorId
    if (!nome.trim() || !periodo.trim() || !responsavelId) return
    setErro(null)
    setCriando(true)
    try {
      await criarTurma({ nome, periodo, professor_responsavel_id: responsavelId })
      await queryClient.invalidateQueries({ queryKey: ['turmas'] })
      setDialogoAberto(false)
      setNome('')
      setPeriodo('')
      setProfessorId('')
      toast({ tipo: 'sucesso', titulo: 'Turma criada' })
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setCriando(false)
    }
  }

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>Turmas</h1>
          <p>{usuario?.papel === 'professor' ? 'Turmas sob sua responsabilidade.' : 'Todas as turmas da instituição.'}</p>
        </div>
        <Dialog
          open={dialogoAberto}
          onOpenChange={setDialogoAberto}
          titulo="Nova turma"
          trigger={<Button>Nova turma</Button>}
        >
          <div className="gestao-form">
            <Field label="Nome" htmlFor="turma-nome" obrigatorio>
              <Input id="turma-nome" value={nome} onChange={(e) => setNome(e.target.value)} />
            </Field>
            <Field label="Período" htmlFor="turma-periodo" dica="Ex: 2026.1" obrigatorio>
              <Input id="turma-periodo" value={periodo} onChange={(e) => setPeriodo(e.target.value)} />
            </Field>
            {usuario?.papel !== 'professor' && (
              <Field label="Professor responsável" htmlFor="turma-professor" obrigatorio>
                <Select
                  id="turma-professor"
                  value={professorId}
                  onValueChange={setProfessorId}
                  opcoes={professores.map((p) => ({ value: p.id, label: p.nome }))}
                  placeholder="Selecione um professor"
                />
              </Field>
            )}
            {erro && <p className="field__erro" role="alert">{erro}</p>}
            <Button carregando={criando} onClick={() => void handleCriar()}>
              Criar turma
            </Button>
          </div>
        </Dialog>
      </header>

      {turmasQuery.isLoading && <PageSpinner />}
      {turmasQuery.isError && (
        <ErrorState mensagem={paraErroApi(turmasQuery.error).message} onRetry={() => turmasQuery.refetch()} />
      )}
      {turmasQuery.data && (
        <Table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Período</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {turmasQuery.data.map((t) => (
              <tr key={t.id}>
                <td>
                  <Link to={`/gestao/turmas/${t.id}`}>{t.nome}</Link>
                </td>
                <td>{t.periodo}</td>
                <td>
                  <Badge tom={t.ativo ? 'sucesso' : 'neutro'}>{t.ativo ? 'Ativa' : 'Inativa'}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}
