import { useQuery } from '@tanstack/react-query'
import { Swords } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { Select } from '@/components/ui/Select'
import { PageSpinner, Spinner } from '@/components/ui/Spinner'
import { paraErroApi } from '@/lib/api/errors'
import { listarMinhasTurmas } from '@/lib/api/turmas'
import { useAuth } from '@/lib/auth/useAuth'
import { useBatalhaSocket } from '@/lib/battle/useBatalhaSocket'
import './BatalhaPage.css'

/** Batalha 1x1 entre colegas online na mesma turma
 * (docs/prompt-redesign-frontend.md §3.6), via o battle-service (WebSocket,
 * processo separado - ver battle-service/README.md). O pareamento em si é
 * real; a partida (problema/submissão) ainda não tem rota no backend
 * principal, então ao iniciar uma batalha isso fica sinalizado, sem
 * simular um jogo. */
export function BatalhaPage() {
  const { usuario } = useAuth()
  const turmasQuery = useQuery({ queryKey: ['minhas-turmas'], queryFn: listarMinhasTurmas })
  const [turmaEscolhidaId, setTurmaEscolhidaId] = useState<string | null>(null)
  // Turma única: nada a escolher, já usa ela; múltiplas turmas dependem da
  // escolha explícita no <Select> abaixo.
  const turmaId =
    turmaEscolhidaId ?? (turmasQuery.data?.length === 1 ? turmasQuery.data[0].id : null)

  const { status, oponente, iniciarBusca, cancelarBusca, responder } = useBatalhaSocket(
    turmaId,
    usuario?.nome ?? null,
  )

  const turmaSelecionada = turmasQuery.data?.find((t) => t.id === turmaId)

  return (
    <div className="batalha-page">
      <h1>Batalha</h1>

      {turmasQuery.isLoading && <PageSpinner />}
      {turmasQuery.isError && (
        <ErrorState mensagem={paraErroApi(turmasQuery.error).message} onRetry={() => turmasQuery.refetch()} />
      )}
      {turmasQuery.data && turmasQuery.data.length === 0 && (
        <EmptyState
          titulo="Você ainda não está em nenhuma turma"
          descricao="Batalhas acontecem entre colegas da mesma turma. Peça ao seu professor a matrícula na turma primeiro."
          acao={<Swords size={22} style={{ color: 'var(--text-muted)' }} />}
        />
      )}

      {turmasQuery.data && turmasQuery.data.length > 0 && (
        <Card className="batalha-page__card">
          {turmasQuery.data.length > 1 && status === 'ocioso' && (
            <div className="batalha-page__campo">
              <label htmlFor="batalha-turma">Turma</label>
              <Select
                id="batalha-turma"
                value={turmaId ?? ''}
                onValueChange={setTurmaEscolhidaId}
                placeholder="Escolha a turma"
                opcoes={turmasQuery.data.map((t) => ({ value: t.id, label: t.nome }))}
              />
            </div>
          )}

          {status === 'ocioso' && (
            <div className="batalha-page__estado">
              <Swords size={28} style={{ color: 'var(--text-muted)' }} aria-hidden="true" />
              <p>Desafie um colega online {turmaSelecionada ? `da turma ${turmaSelecionada.nome}` : 'da mesma turma'}.</p>
              <Button onClick={iniciarBusca} disabled={!turmaId}>
                Buscar oponente
              </Button>
            </div>
          )}

          {(status === 'conectando' || status === 'procurando') && (
            <div className="batalha-page__estado">
              <Spinner tamanho={26} />
              <p>Procurando um colega online{turmaSelecionada ? ` na turma ${turmaSelecionada.nome}` : ''}…</p>
              <Button variante="secundario" onClick={cancelarBusca}>
                Cancelar
              </Button>
            </div>
          )}

          {status === 'convite' && oponente && (
            <div className="batalha-page__estado">
              <Badge tom="accent">Desafio recebido</Badge>
              <p>
                <strong>{oponente.nome}</strong> está online e disponível para batalhar. Aceitar?
              </p>
              <div className="batalha-page__acoes">
                <Button variante="secundario" onClick={() => responder(false)}>
                  Recusar
                </Button>
                <Button onClick={() => responder(true)}>Aceitar</Button>
              </div>
            </div>
          )}

          {status === 'aguardando_oponente' && (
            <div className="batalha-page__estado">
              <Spinner tamanho={26} />
              <p>Você aceitou! Aguardando {oponente?.nome ?? 'o colega'} confirmar…</p>
              <Button variante="secundario" onClick={cancelarBusca}>
                Cancelar
              </Button>
            </div>
          )}

          {status === 'iniciada' && (
            <div className="batalha-page__estado">
              <Badge tom="sucesso">Batalha iniciada</Badge>
              <p>
                Você e <strong>{oponente?.nome ?? 'seu colega'}</strong> topam o desafio!
              </p>
              <p className="batalha-page__nota">
                A partida em si (problema sorteado, submissão de código) ainda depende de uma rota
                que o backend principal ainda não expõe — por enquanto, só o convite entre vocês é
                real.
              </p>
              <Button variante="secundario" onClick={cancelarBusca}>
                Concluir
              </Button>
            </div>
          )}

          {status === 'erro' && (
            <ErrorState
              mensagem="Não foi possível conectar ao serviço de batalhas."
              onRetry={iniciarBusca}
            />
          )}
        </Card>
      )}
    </div>
  )
}
