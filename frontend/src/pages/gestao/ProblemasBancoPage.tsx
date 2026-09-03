import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { Table } from '@/components/ui/Table'
import { paraErroApi } from '@/lib/api/errors'
import { listarProblemas } from '@/lib/api/problemas'
import { NIVEL_DIFICULDADE_LABEL, type NivelDificuldade } from '@/lib/api/types'
import './DashboardTurmasPage.css'

const TOM: Record<NivelDificuldade, 'sucesso' | 'aviso' | 'erro'> = {
  facil: 'sucesso',
  medio: 'aviso',
  dificil: 'erro',
}

export function ProblemasBancoPage() {
  const problemasQuery = useQuery({ queryKey: ['problemas'], queryFn: listarProblemas })

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>Banco de problemas</h1>
          <p>Problemas cadastrados na sua instituição.</p>
        </div>
        <Link to="/gestao/problemas/novo">
          <Button>Novo problema</Button>
        </Link>
      </header>

      {problemasQuery.isLoading && <PageSpinner />}
      {problemasQuery.isError && (
        <ErrorState mensagem={paraErroApi(problemasQuery.error).message} onRetry={() => problemasQuery.refetch()} />
      )}
      {problemasQuery.data && (
        <Table>
          <thead>
            <tr>
              <th>Título</th>
              <th>Nível</th>
              <th>Linguagem</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody>
            {problemasQuery.data.map((p) => (
              <tr key={p.id}>
                <td>
                  <Link to={`/gestao/problemas/${p.id}`}>{p.titulo}</Link>
                </td>
                <td>
                  <Badge tom={TOM[p.nivel_dificuldade]}>{NIVEL_DIFICULDADE_LABEL[p.nivel_dificuldade]}</Badge>
                </td>
                <td>{p.linguagem}</td>
                <td>{p.tags.map((t) => t.nome).join(', ') || '—'}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}
