import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, XCircle } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { paraErroApi } from '@/lib/api/errors'
import { listarDicasDeAluno } from '@/lib/api/dicas'
import { obterProblema } from '@/lib/api/problemas'
import { NIVEL_DICA_LABEL } from '@/lib/api/types'
import './PainelDicasAlunoPage.css'

/** Painel pedagógico: histórico de dicas + adaptações aplicadas + eficácia
 * (tempo até resolver). Nunca exposto ao aluno - só Professor+
 * (docs/prompt-redesign-frontend.md §2.2, GET /problemas/{id}/dicas/{aluno_id}). */
export function PainelDicasAlunoPage() {
  const { problemaId, alunoId } = useParams<{ problemaId: string; alunoId: string }>()

  const problemaQuery = useQuery({ queryKey: ['problema', problemaId], queryFn: () => obterProblema(problemaId!) })
  const dicasQuery = useQuery({
    queryKey: ['dicas-aluno', problemaId, alunoId],
    queryFn: () => listarDicasDeAluno(problemaId!, alunoId!),
  })

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>Dicas e eficácia</h1>
          <p>
            {problemaQuery.data?.titulo ?? 'Problema'} · aluno <code>{alunoId}</code>
          </p>
        </div>
      </header>

      {dicasQuery.isLoading && <PageSpinner />}
      {dicasQuery.isError && (
        <ErrorState mensagem={paraErroApi(dicasQuery.error).message} onRetry={() => dicasQuery.refetch()} />
      )}
      {dicasQuery.data && dicasQuery.data.length === 0 && (
        <EmptyState titulo="Nenhuma dica pedida" descricao="Este aluno ainda não pediu dicas para este problema." />
      )}

      {dicasQuery.data && dicasQuery.data.length > 0 && (
        <ol className="painel-dicas__lista">
          {dicasQuery.data.map((dica) => (
            <li key={dica.id} className="painel-dicas__item">
              <div className="painel-dicas__cabecalho">
                <span>
                  Nível {dica.nivel} — {NIVEL_DICA_LABEL[dica.nivel]}
                </span>
                <Badge tom={dica.resolvida_apos ? 'sucesso' : 'neutro'}>
                  {dica.resolvida_apos ? (
                    <>
                      <CheckCircle2 size={12} /> resolveu depois
                    </>
                  ) : (
                    <>
                      <XCircle size={12} /> não resolveu ainda
                    </>
                  )}
                </Badge>
              </div>
              <p>{dica.conteudo}</p>
              {dica.adaptacoes_aplicadas.length > 0 && (
                <div className="painel-dicas__adaptacoes">
                  {dica.adaptacoes_aplicadas.map((a) => (
                    <Badge key={a} tom="accent">
                      {a}
                    </Badge>
                  ))}
                </div>
              )}
              {dica.tempo_ate_resolver_ms !== null && (
                <p className="painel-dicas__tempo">
                  Tempo até resolver após esta dica: {(dica.tempo_ate_resolver_ms / 1000).toFixed(0)} s
                </p>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
