import { useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, GitBranch, Headphones, ListChecks, Map as MapIcon } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { DicasPanel } from './DicasPanel'
import { ResultadoCasoCard } from './ResultadoCasoCard'
import { CodeEditor } from '@/components/code/CodeEditor'
import { Badge } from '@/components/ui/Badge'
import { BotaoOuvir } from '@/components/ui/BotaoOuvir'
import { Button } from '@/components/ui/Button'
import { ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner, Spinner } from '@/components/ui/Spinner'
import { Tabs } from '@/components/ui/Tabs'
import { paraErroApi } from '@/lib/api/errors'
import { listarMinhasSubmissoes, obterProblema, submeterCodigo } from '@/lib/api/problemas'
import { NIVEL_DIFICULDADE_LABEL, STATUS_SUBMISSAO_LABEL, type NivelDificuldade, type StatusSubmissao, type SubmissaoResponse } from '@/lib/api/types'
import './ProblemaPage.css'

const TOM_DIFICULDADE: Record<NivelDificuldade, 'sucesso' | 'aviso' | 'erro'> = {
  facil: 'sucesso',
  medio: 'aviso',
  dificil: 'erro',
}
const TOM_STATUS: Record<StatusSubmissao, 'sucesso' | 'erro'> = {
  aceito: 'sucesso',
  reprovado: 'erro',
  erro_execucao: 'erro',
  tempo_excedido: 'erro',
  erro_interno: 'erro',
}

type FormatoEstudo = 'texto' | 'passos' | 'mapa' | 'audio'

export function ProblemaPage() {
  const { problemaId } = useParams<{ problemaId: string }>()
  const queryClient = useQueryClient()

  const [aba, setAba] = useState('enunciado')
  const [formato, setFormato] = useState<FormatoEstudo>('texto')
  const [codigo, setCodigo] = useState('')
  const [submetendo, setSubmetendo] = useState(false)
  const [erroSubmissao, setErroSubmissao] = useState<string | null>(null)
  const [ultimoResultado, setUltimoResultado] = useState<SubmissaoResponse | null>(null)

  const problemaQuery = useQuery({
    queryKey: ['problema', problemaId],
    queryFn: () => obterProblema(problemaId!),
  })
  const submissoesQuery = useQuery({
    queryKey: ['minhas-submissoes', problemaId],
    queryFn: () => listarMinhasSubmissoes(problemaId!),
    enabled: aba === 'submissoes',
  })

  if (problemaQuery.isLoading) return <PageSpinner />
  if (problemaQuery.isError) {
    return <ErrorState mensagem={paraErroApi(problemaQuery.error).message} onRetry={() => problemaQuery.refetch()} />
  }
  const problema = problemaQuery.data!

  async function handleSubmeter() {
    if (!codigo.trim()) return
    setErroSubmissao(null)
    setSubmetendo(true)
    try {
      const resultado = await submeterCodigo(problemaId!, { codigo_fonte: codigo })
      setUltimoResultado(resultado)
      await queryClient.invalidateQueries({ queryKey: ['minhas-submissoes', problemaId] })
    } catch (erro) {
      const e = paraErroApi(erro)
      if (e.code === 'unknown' && e.status === null) {
        setErroSubmissao('A execução demorou mais do que o esperado ou a conexão foi perdida. Tente novamente.')
      } else {
        setErroSubmissao(e.message)
      }
    } finally {
      setSubmetendo(false)
    }
  }

  return (
    <div className="problema-pagina">
      <header className="problema-pagina__topo">
        <div>
          <h1>{problema.titulo}</h1>
          <div className="problema-pagina__badges">
            <Badge tom={TOM_DIFICULDADE[problema.nivel_dificuldade]}>
              {NIVEL_DIFICULDADE_LABEL[problema.nivel_dificuldade]}
            </Badge>
            {problema.tags.map((t) => (
              <Badge key={t.id} tom="neutro">
                {t.nome}
              </Badge>
            ))}
          </div>
        </div>
      </header>

      <Tabs
        value={aba}
        onValueChange={setAba}
        abas={[
          {
            value: 'enunciado',
            label: 'Enunciado e código',
            conteudo: (
              <div className="problema-pagina__grid">
                <div className="problema-pagina__enunciado">
                  <div className="problema-pagina__formato" role="tablist" aria-label="Formato de estudo">
                    <FormatoBotao ativo={formato === 'texto'} onClick={() => setFormato('texto')} icone={<ListChecks size={14} />} texto="Texto" />
                    <FormatoBotao ativo={formato === 'passos'} onClick={() => setFormato('passos')} icone={<GitBranch size={14} />} texto="Passo a passo" />
                    <FormatoBotao ativo={formato === 'mapa'} onClick={() => setFormato('mapa')} icone={<MapIcon size={14} />} texto="Mapa mental" />
                    <FormatoBotao ativo={formato === 'audio'} onClick={() => setFormato('audio')} icone={<Headphones size={14} />} texto="Vídeo/áudio" />
                  </div>

                  {formato === 'texto' ? (
                    <>
                      <div className="problema-pagina__ouvir">
                        <BotaoOuvir texto={problema.enunciado} />
                      </div>
                      <p className="problema-pagina__texto">{problema.enunciado}</p>
                      {problema.casos.filter((c) => c.publico).length > 0 && (
                        <div className="problema-pagina__casos-publicos">
                          <h2>Exemplos</h2>
                          {problema.casos
                            .filter((c) => c.publico)
                            .map((c) => (
                              <div key={c.id} className="problema-pagina__caso-exemplo">
                                <code>entrada: {c.entrada || '(vazia)'}</code>
                                <code>saída: {c.saida_esperada}</code>
                              </div>
                            ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="problema-pagina__formato-pendente">
                      <AlertCircle size={16} />
                      <p>
                        Este formato de conteúdo ainda depende de material que o backend não gera
                        automaticamente a partir do enunciado. Em breve, quando essa adaptação
                        estiver disponível, ela aparece aqui sem exigir nenhuma ação sua.
                      </p>
                    </div>
                  )}
                </div>

                <div className="problema-pagina__codigo">
                  <CodeEditor value={codigo} onChange={setCodigo} />
                  <div className="problema-pagina__acoes-codigo">
                    <Button onClick={() => void handleSubmeter()} carregando={submetendo} disabled={!codigo.trim()}>
                      {submetendo ? 'Executando…' : 'Enviar solução'}
                    </Button>
                    {submetendo && (
                      <span className="problema-pagina__executando">
                        <Spinner tamanho={14} /> Rodando seu código no sandbox…
                      </span>
                    )}
                  </div>
                  {erroSubmissao && (
                    <p className="field__erro" role="alert">
                      {erroSubmissao}
                    </p>
                  )}
                  {ultimoResultado && (
                    <div className="problema-pagina__resultado">
                      <div className="problema-pagina__resultado-cabecalho">
                        <Badge tom={TOM_STATUS[ultimoResultado.status]}>{STATUS_SUBMISSAO_LABEL[ultimoResultado.status]}</Badge>
                        <span>{ultimoResultado.tempo_execucao_ms} ms</span>
                      </div>
                      {ultimoResultado.resultados.map((r, i) => (
                        <ResultadoCasoCard key={r.caso_teste_id} resultado={r} indice={i} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ),
          },
          {
            value: 'dicas',
            label: 'Dicas',
            conteudo: <DicasPanel problemaId={problemaId!} />,
          },
          {
            value: 'submissoes',
            label: 'Minhas submissões',
            conteudo: (
              <div className="problema-pagina__submissoes">
                {submissoesQuery.isLoading && <PageSpinner />}
                {submissoesQuery.data && submissoesQuery.data.length === 0 && (
                  <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>
                    Você ainda não enviou nenhuma solução para este problema.
                  </p>
                )}
                {submissoesQuery.data && submissoesQuery.data.length > 0 && (
                  <ul className="problema-pagina__lista-submissoes">
                    {submissoesQuery.data.map((s) => (
                      <li key={s.id}>
                        <Badge tom={TOM_STATUS[s.status]}>{STATUS_SUBMISSAO_LABEL[s.status]}</Badge>
                        <span>{new Date(s.criado_em).toLocaleString('pt-BR')}</span>
                        <span className="problema-pagina__submissao-tempo">{s.tempo_execucao_ms} ms</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ),
          },
        ]}
      />
    </div>
  )
}

function FormatoBotao({
  ativo,
  onClick,
  icone,
  texto,
}: {
  ativo: boolean
  onClick: () => void
  icone: ReactNode
  texto: string
}) {
  return (
    <button type="button" className="problema-pagina__formato-botao" data-ativo={ativo} onClick={onClick} role="tab" aria-selected={ativo}>
      {icone}
      {texto}
    </button>
  )
}
