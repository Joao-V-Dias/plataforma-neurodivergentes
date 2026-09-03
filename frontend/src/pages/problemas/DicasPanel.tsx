import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Lightbulb } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { BotaoOuvir } from '@/components/ui/BotaoOuvir'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { PageSpinner } from '@/components/ui/Spinner'
import { paraErroApi } from '@/lib/api/errors'
import { listarMinhasDicas, pedirDica } from '@/lib/api/dicas'
import { NIVEL_DICA_LABEL } from '@/lib/api/types'
import './DicasPanel.css'

const NIVEL_MAXIMO = 4

export function DicasPanel({ problemaId }: { problemaId: string }) {
  const queryClient = useQueryClient()
  const [pedindo, setPedindo] = useState(false)
  const [avisoNivelMaximo, setAvisoNivelMaximo] = useState(false)
  const [iaIndisponivel, setIaIndisponivel] = useState(false)

  const dicasQuery = useQuery({
    queryKey: ['minhas-dicas', problemaId],
    queryFn: () => listarMinhasDicas(problemaId),
  })

  const dicas = dicasQuery.data ?? []
  const proximoNivel = dicas.length + 1
  const noNivelMaximo = dicas.length >= NIVEL_MAXIMO

  async function handlePedirDica() {
    setAvisoNivelMaximo(false)
    setIaIndisponivel(false)
    setPedindo(true)
    try {
      await pedirDica(problemaId)
      await queryClient.invalidateQueries({ queryKey: ['minhas-dicas', problemaId] })
    } catch (erro) {
      const e = paraErroApi(erro)
      if (e.code === 'conflict') setAvisoNivelMaximo(true)
      else if (e.code === 'service_unavailable') setIaIndisponivel(true)
    } finally {
      setPedindo(false)
    }
  }

  return (
    <div className="dicas-painel">
      <p className="dicas-painel__intro">
        Dicas progressivas: cada pedido revela um nível a mais de ajuda, começando por uma pergunta
        que te leva a pensar, até uma solução comentada. Pedir uma dica não afeta sua nota.
      </p>

      {dicasQuery.isLoading && <PageSpinner />}
      {dicasQuery.isError && (
        <ErrorState mensagem={paraErroApi(dicasQuery.error).message} onRetry={() => dicasQuery.refetch()} />
      )}
      {dicasQuery.data && dicas.length === 0 && !dicasQuery.isLoading && (
        <EmptyState titulo="Nenhuma dica pedida ainda" descricao="Tente resolver por conta própria primeiro — você pode pedir ajuda a qualquer momento." />
      )}

      {dicas.length > 0 && (
        <ol className="dicas-painel__lista">
          {dicas.map((dica) => (
            <li key={dica.id} className="dicas-painel__item">
              <div className="dicas-painel__item-cabecalho">
                <Lightbulb size={14} />
                <span>
                  Nível {dica.nivel} — {NIVEL_DICA_LABEL[dica.nivel]}
                </span>
              </div>
              <p>{dica.conteudo}</p>
              <BotaoOuvir texto={dica.conteudo} />
            </li>
          ))}
        </ol>
      )}

      {iaIndisponivel && (
        <p className="dicas-painel__aviso" role="alert">
          O gerador de dicas está indisponível no momento. Você pode continuar submetendo seu
          código normalmente e tentar pedir a dica novamente em instantes.
        </p>
      )}
      {avisoNivelMaximo && (
        <p className="dicas-painel__aviso" role="status">
          Você já recebeu todas as dicas disponíveis para este problema.
        </p>
      )}

      {!noNivelMaximo && (
        <Button variante="secundario" carregando={pedindo} onClick={() => void handlePedirDica()}>
          Pedir dica (nível {proximoNivel})
        </Button>
      )}
    </div>
  )
}
