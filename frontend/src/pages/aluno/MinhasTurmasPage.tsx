import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Pin } from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { listarMinhasTurmas } from '@/lib/api/turmas'
import { obterPerfilAluno } from '@/lib/api/perfis'
import { paraErroApi } from '@/lib/api/errors'
import { useAuth } from '@/lib/auth/useAuth'
import './MinhasTurmasPage.css'

const DATA_HOJE = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
const SEGMENTOS_BANDA = [0, 1, 2, 3, 4]

function BandaIntensidade({ ligado }: { ligado: boolean }) {
  return (
    <span className="minhas-turmas__banda" data-ligado={ligado} aria-hidden="true">
      {SEGMENTOS_BANDA.map((segmento) => (
        <span key={segmento} className="minhas-turmas__banda-segmento" />
      ))}
    </span>
  )
}

export function MinhasTurmasPage() {
  const { usuario } = useAuth()
  const turmasQuery = useQuery({ queryKey: ['minhas-turmas'], queryFn: listarMinhasTurmas })
  const perfilQuery = useQuery({
    queryKey: ['meu-perfil-aluno', usuario?.id],
    queryFn: () => obterPerfilAluno(usuario!.id),
    enabled: !!usuario,
    retry: false,
  })
  const perfilAusente = perfilQuery.isError && paraErroApi(perfilQuery.error).code === 'not_found'

  const totalTurmas = turmasQuery.data?.length ?? 0
  const totalAtivas = turmasQuery.data?.filter((turma) => turma.ativo).length ?? 0

  return (
    <div className="minhas-turmas">
      <header className="minhas-turmas__topo">
        <div>
          <h1>Minhas turmas</h1>
          <p className="minhas-turmas__data">{DATA_HOJE.format(new Date())}</p>
        </div>
        {turmasQuery.data && turmasQuery.data.length > 0 && (
          <div className="minhas-turmas__leitura" role="status">
            <span className="minhas-turmas__leitura-valor">{totalAtivas}</span>
            <span className="minhas-turmas__leitura-rotulo">
              de {totalTurmas} estaç{totalTurmas === 1 ? 'ão' : 'ões'} ativa{totalAtivas === 1 ? '' : 's'}
            </span>
          </div>
        )}
      </header>

      {perfilAusente && (
        <Link to="/onboarding" className="minhas-turmas__nota">
          <Pin size={14} aria-hidden="true" />
          <span>Complete seu perfil para receber um ensino mais adaptado a você.</span>
          <ArrowRight size={14} />
        </Link>
      )}

      {turmasQuery.isLoading && <PageSpinner />}
      {turmasQuery.isError && (
        <ErrorState mensagem={paraErroApi(turmasQuery.error).message} onRetry={() => turmasQuery.refetch()} />
      )}
      {turmasQuery.data && turmasQuery.data.length === 0 && (
        <EmptyState
          titulo="Você ainda não está em nenhuma turma"
          descricao="Peça ao seu professor o código da instituição e a matrícula na turma."
        />
      )}

      {turmasQuery.data && turmasQuery.data.length > 0 && (
        <ol className="minhas-turmas__painel">
          <li className="minhas-turmas__cabecalho-lista" aria-hidden="true">
            <span className="minhas-turmas__col-estacao">Estação</span>
            <span className="minhas-turmas__col-nome">Turma</span>
            <span className="minhas-turmas__col-periodo">Período</span>
            <span className="minhas-turmas__col-status">Status</span>
          </li>
          {turmasQuery.data.map((turma, indice) => (
            <li key={turma.id} className="minhas-turmas__entrada">
              <Link to={`/turmas/${turma.id}/mapa`} className="minhas-turmas__linha">
                <span className="minhas-turmas__estacao">
                  <span
                    className="minhas-turmas__led"
                    data-ligado={turma.ativo}
                    aria-hidden="true"
                  />
                  {String(indice + 1).padStart(2, '0')}
                </span>
                <span className="minhas-turmas__nome">{turma.nome}</span>
                <span className="minhas-turmas__periodo">{turma.periodo}</span>
                <span className="minhas-turmas__leitura-estacao">
                  <BandaIntensidade ligado={turma.ativo} />
                  <span className="minhas-turmas__status" data-ligado={turma.ativo}>
                    {turma.ativo ? 'em curso' : 'encerrada'}
                  </span>
                </span>
                <span className="minhas-turmas__abrir" aria-hidden="true">
                  <span className="minhas-turmas__abrir-rotulo">abrir</span>
                  <ArrowRight size={16} className="minhas-turmas__seta" />
                </span>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
