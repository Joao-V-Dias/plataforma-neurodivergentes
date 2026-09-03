import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { Table } from '@/components/ui/Table'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import { aprovarUsuario, listarUsuarios } from '@/lib/api/usuarios'
import './DashboardTurmasPage.css'

export function FilaAprovacaoPage() {
  const queryClient = useQueryClient()
  const usuariosQuery = useQuery({ queryKey: ['usuarios'], queryFn: () => listarUsuarios() })
  const pendentes = (usuariosQuery.data ?? []).filter((u) => !u.is_active)

  async function aprovar(id: string) {
    try {
      await aprovarUsuario(id)
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      toast({ tipo: 'sucesso', titulo: 'Conta aprovada' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível aprovar', descricao: paraErroApi(e).message })
    }
  }

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>Aprovações pendentes</h1>
          <p>Contas de alunos que se auto-cadastraram e aguardam liberação.</p>
        </div>
      </header>

      {usuariosQuery.isLoading && <PageSpinner />}
      {usuariosQuery.isError && (
        <ErrorState mensagem={paraErroApi(usuariosQuery.error).message} onRetry={() => usuariosQuery.refetch()} />
      )}
      {usuariosQuery.data && pendentes.length === 0 && (
        <EmptyState titulo="Nenhuma aprovação pendente" descricao="Todas as contas desta instituição já foram revisadas." />
      )}
      {pendentes.length > 0 && (
        <Table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Cadastrado em</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {pendentes.map((u) => (
              <tr key={u.id}>
                <td>{u.nome}</td>
                <td>{u.email}</td>
                <td>{new Date(u.created_at).toLocaleDateString('pt-BR')}</td>
                <td>
                  <Button tamanho="sm" onClick={() => void aprovar(u.id)}>
                    Aprovar
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}
