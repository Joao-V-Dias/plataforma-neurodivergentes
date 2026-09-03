import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { Select } from '@/components/ui/Select'
import { PageSpinner } from '@/components/ui/Spinner'
import { paraErroApi } from '@/lib/api/errors'
import { listarProblemasDaTurma, listarTags } from '@/lib/api/problemas'
import { obterTurma } from '@/lib/api/turmas'
import { NIVEL_DIFICULDADE_LABEL, type NivelDificuldade } from '@/lib/api/types'
import './MapaDoJogoPage.css'

const TOM_DIFICULDADE: Record<NivelDificuldade, 'sucesso' | 'aviso' | 'erro'> = {
  facil: 'sucesso',
  medio: 'aviso',
  dificil: 'erro',
}

export function MapaDoJogoPage() {
  const { turmaId } = useParams<{ turmaId: string }>()
  const [filtroTag, setFiltroTag] = useState('todos')

  const turmaQuery = useQuery({ queryKey: ['turma', turmaId], queryFn: () => obterTurma(turmaId!) })
  const problemasQuery = useQuery({
    queryKey: ['turma-problemas', turmaId],
    queryFn: () => listarProblemasDaTurma(turmaId!),
  })
  const tagsQuery = useQuery({ queryKey: ['tags'], queryFn: listarTags })

  const problemasFiltrados = useMemo(() => {
    if (!problemasQuery.data) return []
    if (filtroTag === 'todos') return problemasQuery.data
    return problemasQuery.data.filter((p) => p.tags.some((t) => t.codigo === filtroTag))
  }, [problemasQuery.data, filtroTag])

  return (
    <div className="mapa-jogo">
      <header className="mapa-jogo__topo">
        <div>
          <h1>{turmaQuery.data?.nome ?? 'Mapa do jogo'}</h1>
          <p>Cada fase é um problema. Siga em ordem ou explore livremente — você escolhe.</p>
        </div>
        {tagsQuery.data && tagsQuery.data.length > 0 && (
          <div className="mapa-jogo__filtro">
            <Select
              value={filtroTag}
              onValueChange={setFiltroTag}
              opcoes={[{ value: 'todos', label: 'Todos os temas' }, ...tagsQuery.data.map((t) => ({ value: t.codigo, label: t.nome }))]}
            />
          </div>
        )}
      </header>

      {problemasQuery.isLoading && <PageSpinner />}
      {problemasQuery.isError && (
        <ErrorState mensagem={paraErroApi(problemasQuery.error).message} onRetry={() => problemasQuery.refetch()} />
      )}
      {problemasQuery.data && problemasFiltrados.length === 0 && (
        <EmptyState titulo="Nenhum problema disponível" descricao="Ainda não há problemas vinculados a esta turma." />
      )}

      {problemasFiltrados.length > 0 && (
        <ol className="mapa-jogo__trilha">
          {problemasFiltrados.map((problema, i) => (
            <li key={problema.id} className="mapa-jogo__fase">
              <span className="mapa-jogo__numero">{i + 1}</span>
              <Link to={`/turmas/${turmaId}/problemas/${problema.id}`} className="mapa-jogo__link">
                <span className="mapa-jogo__titulo">{problema.titulo}</span>
                <span className="mapa-jogo__meta">
                  <Badge tom={TOM_DIFICULDADE[problema.nivel_dificuldade]}>
                    {NIVEL_DIFICULDADE_LABEL[problema.nivel_dificuldade]}
                  </Badge>
                  {problema.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag.id} tom="neutro">
                      {tag.nome}
                    </Badge>
                  ))}
                </span>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
