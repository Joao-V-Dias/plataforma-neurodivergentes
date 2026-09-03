import { useQuery } from '@tanstack/react-query'
import { Flame, ListChecks, Timer, Trophy } from 'lucide-react'
import type { ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { paraErroApi } from '@/lib/api/errors'
import { listarMeusEmblemas, obterMinhaPontuacao } from '@/lib/api/gamificacao'
import { obterMeuProgresso } from '@/lib/api/turmas'
import './MeuProgressoPage.css'

export function MeuProgressoPage() {
  const { turmaId } = useParams<{ turmaId: string }>()

  const progressoQuery = useQuery({
    queryKey: ['meu-progresso', turmaId],
    queryFn: () => obterMeuProgresso(turmaId!),
  })
  const pontuacaoQuery = useQuery({ queryKey: ['minha-pontuacao'], queryFn: obterMinhaPontuacao })
  const emblemasQuery = useQuery({ queryKey: ['meus-emblemas'], queryFn: listarMeusEmblemas })

  if (progressoQuery.isLoading) return <PageSpinner />
  if (progressoQuery.isError) {
    return <ErrorState mensagem={paraErroApi(progressoQuery.error).message} onRetry={() => progressoQuery.refetch()} />
  }
  const progresso = progressoQuery.data!
  const pontuacao = pontuacaoQuery.data

  return (
    <div className="meu-progresso">
      <h1>Meu progresso</h1>
      <div className="meu-progresso__metricas">
        <Metrica icone={<ListChecks size={18} />} rotulo="Problemas resolvidos" valor={progresso.problemas_resolvidos} />
        <Metrica icone={<Timer size={18} />} rotulo="Tempo dedicado" valor={`${progresso.tempo_gasto_minutos} min`} />
        {pontuacao && <Metrica icone={<Trophy size={18} />} rotulo="Pontos" valor={pontuacao.pontos} tom="yellow" />}
        {pontuacao && <Metrica icone={<Flame size={18} />} rotulo="Sequência atual" valor={`${pontuacao.sequencia_dias} dias`} tom="orange" />}
      </div>

      {pontuacao && (
        <p className="meu-progresso__nota">
          Maior sequência já alcançada: {pontuacao.maior_sequencia_dias} dias · {progresso.tentativas} tentativas
          registradas nesta turma.
        </p>
      )}

      <section className="meu-progresso__emblemas">
        <h2>Emblemas conquistados</h2>
        {emblemasQuery.data && emblemasQuery.data.length === 0 && (
          <p className="meu-progresso__vazio">Nenhum emblema ainda — continue resolvendo problemas para desbloquear os primeiros.</p>
        )}
        {emblemasQuery.data && emblemasQuery.data.length > 0 && (
          <ul className="meu-progresso__lista-emblemas">
            {emblemasQuery.data.map((e) => (
              <li key={e.id} title={e.descricao ?? undefined}>
                <span className="meu-progresso__emblema-nome">{e.nome}</span>
                <span className="meu-progresso__emblema-data">{new Date(e.conquistado_em).toLocaleDateString('pt-BR')}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="meu-progresso__ranking-aviso">
        Ranking entre colegas ainda não está disponível — esta comparação depende de uma rota que o
        backend ainda não expõe.
      </p>
    </div>
  )
}

function Metrica({
  icone,
  rotulo,
  valor,
  tom,
}: {
  icone: ReactNode
  rotulo: string
  valor: string | number
  tom?: 'yellow' | 'orange'
}) {
  return (
    <div className="meu-progresso__metrica">
      <span className={`meu-progresso__metrica-icone${tom ? ` meu-progresso__metrica-icone--${tom}` : ''}`}>{icone}</span>
      <div>
        <p className="meu-progresso__metrica-valor">{valor}</p>
        <p className="meu-progresso__metrica-rotulo">{rotulo}</p>
      </div>
    </div>
  )
}
