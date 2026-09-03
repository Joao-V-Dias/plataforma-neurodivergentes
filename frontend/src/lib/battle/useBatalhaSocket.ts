import { useCallback, useEffect, useRef, useState } from 'react'
import { garantirAccessTokenValido } from '@/lib/api/client'

/** Cliente do battle-service (battle-service/, processo separado da API
 * principal - ver battle-service/README.md para o protocolo). Sugestao de
 * batalha 1x1 entre alunos online na mesma turma
 * (docs/prompt-redesign-frontend.md #3.6). */

const WS_BASE_URL =
  (import.meta.env.VITE_BATTLE_WS_URL as string | undefined) ?? 'ws://127.0.0.1:8001'

export type StatusBatalha =
  | 'ocioso'
  | 'conectando'
  | 'procurando'
  | 'convite'
  | 'aguardando_oponente'
  | 'iniciada'
  | 'erro'

export interface OponenteBatalha {
  id: string
  nome: string
}

interface MensagemServidor {
  tipo: 'batalha_sugerida' | 'batalha_cancelada' | 'batalha_iniciada'
  batalha_id?: string
  oponente?: OponenteBatalha
  oponente_id?: string
  motivo?: string
}

export function useBatalhaSocket(turmaId: string | null, nomeExibicao: string | null) {
  const [status, setStatus] = useState<StatusBatalha>('ocioso')
  const [oponente, setOponente] = useState<OponenteBatalha | null>(null)
  const [batalhaId, setBatalhaId] = useState<string | null>(null)
  const socketRef = useRef<WebSocket | null>(null)
  // Cresce a cada chamada; uma resposta assíncrona (token renovado) só é
  // aplicada se ainda for a tentativa mais recente - evita que um
  // iniciarBusca() atrasado reabra o socket depois de um cancelarBusca().
  const tentativaRef = useRef(0)

  const encerrar = useCallback(() => {
    tentativaRef.current += 1
    socketRef.current?.close()
    socketRef.current = null
    setStatus('ocioso')
    setOponente(null)
    setBatalhaId(null)
  }, [])

  const iniciarBusca = useCallback(() => {
    if (!turmaId || !nomeExibicao) return
    const minhaTentativa = ++tentativaRef.current
    socketRef.current?.close()
    socketRef.current = null
    setStatus('conectando')
    setOponente(null)
    setBatalhaId(null)

    void (async () => {
      // O handshake do WebSocket não passa pelo interceptor de 401 do
      // apiClient - sem isso, um access token expirado (15min) travaria a
      // busca com um 403 silencioso.
      const token = await garantirAccessTokenValido()
      if (tentativaRef.current !== minhaTentativa) return // cancelado enquanto renovava o token
      if (token === null) {
        setStatus('erro')
        return
      }

      const params = new URLSearchParams({ token, nome: nomeExibicao, turma_id: turmaId })
      const socket = new WebSocket(`${WS_BASE_URL}/ws/batalha?${params.toString()}`)
      socketRef.current = socket

      socket.onopen = () => {
        if (tentativaRef.current === minhaTentativa) setStatus('procurando')
      }

      socket.onmessage = (event) => {
        if (tentativaRef.current !== minhaTentativa) return
        const dados = JSON.parse(event.data as string) as MensagemServidor
        if (dados.tipo === 'batalha_sugerida' && dados.oponente && dados.batalha_id) {
          setOponente(dados.oponente)
          setBatalhaId(dados.batalha_id)
          setStatus('convite')
        } else if (dados.tipo === 'batalha_cancelada') {
          setOponente(null)
          setBatalhaId(null)
          setStatus('procurando')
        } else if (dados.tipo === 'batalha_iniciada' && dados.batalha_id) {
          setBatalhaId(dados.batalha_id)
          setStatus('iniciada')
        }
      }

      socket.onerror = () => {
        if (tentativaRef.current === minhaTentativa) setStatus('erro')
      }

      socket.onclose = () => {
        socketRef.current = null
        if (tentativaRef.current === minhaTentativa) {
          setStatus((atual) => (atual === 'erro' ? atual : 'ocioso'))
        }
      }
    })()
  }, [turmaId, nomeExibicao])

  const responder = useCallback(
    (aceitar: boolean) => {
      const socket = socketRef.current
      if (!socket || socket.readyState !== WebSocket.OPEN || !batalhaId) return
      socket.send(JSON.stringify({ tipo: 'responder_batalha', batalha_id: batalhaId, aceitar }))
      setStatus(aceitar ? 'aguardando_oponente' : 'procurando')
      if (!aceitar) {
        setOponente(null)
        setBatalhaId(null)
      }
    },
    [batalhaId],
  )

  useEffect(() => () => socketRef.current?.close(), [])

  return { status, oponente, batalhaId, iniciarBusca, cancelarBusca: encerrar, responder }
}
