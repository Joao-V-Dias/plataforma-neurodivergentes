import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import * as perfisApi from '@/lib/api/perfis'
import type { PreferenciasAcessibilidadeRequest, PreferenciasAcessibilidadeResponse } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'

const PADRAO: PreferenciasAcessibilidadeRequest = {
  fonte_legivel: false,
  alto_contraste: false,
  tempo_extra_percentual: 0,
  leitura_voz_alta: false,
  reducao_estimulos: false,
  tamanho_fonte: 'medio',
}

interface AccessibilityContextValue {
  preferencias: PreferenciasAcessibilidadeRequest
  salvando: boolean
  salvarPreferencias: (payload: PreferenciasAcessibilidadeRequest) => Promise<void>
  /** Lê um texto em voz alta via Web Speech API, só quando o usuário tem
   * `leitura_voz_alta` ativado - usado em botões "ouvir" no enunciado do
   * problema e no conteúdo das dicas (Parte 6), que costumam ser blocos
   * longos de texto. */
  falarTexto: (texto: string) => void
  pararFala: () => void
  suportaLeituraEmVoz: boolean
}

// eslint-disable-next-line react-refresh/only-export-components
export const AccessibilityContext = createContext<AccessibilityContextValue | null>(null)

function aplicarClassesNoDocumento(prefs: PreferenciasAcessibilidadeRequest): void {
  const root = document.documentElement
  root.classList.toggle('a11y-alto-contraste', prefs.alto_contraste)
  root.classList.toggle('a11y-fonte-legivel', prefs.fonte_legivel)
  root.classList.toggle('a11y-reduzir-estimulos', prefs.reducao_estimulos)

  root.classList.remove(
    'a11y-fonte-pequeno',
    'a11y-fonte-medio',
    'a11y-fonte-grande',
    'a11y-fonte-extra_grande',
  )
  root.classList.add(`a11y-fonte-${prefs.tamanho_fonte}`)
}

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const [salvando, setSalvando] = useState(false)
  const suportaLeituraEmVoz = typeof window !== 'undefined' && 'speechSynthesis' in window

  const { data } = useQuery<PreferenciasAcessibilidadeResponse>({
    queryKey: ['preferencias-acessibilidade', usuario?.id],
    queryFn: perfisApi.obterMinhasPreferenciasAcessibilidade,
    enabled: !!usuario,
    staleTime: 5 * 60 * 1000,
  })

  const preferencias = data ?? PADRAO

  useEffect(() => {
    aplicarClassesNoDocumento(preferencias)
  }, [preferencias])

  // Ao deslogar, volta tudo ao padrão em vez de manter o alto-contraste
  // do usuário anterior visível na tela de login do próximo.
  useEffect(() => {
    if (!usuario) aplicarClassesNoDocumento(PADRAO)
  }, [usuario])

  const salvarPreferencias = useCallback(
    async (payload: PreferenciasAcessibilidadeRequest) => {
      setSalvando(true)
      aplicarClassesNoDocumento(payload) // otimista: aplica antes da API confirmar
      try {
        const atualizado = await perfisApi.atualizarPreferenciasAcessibilidade(payload)
        queryClient.setQueryData(['preferencias-acessibilidade', usuario?.id], atualizado)
      } catch (erro) {
        aplicarClassesNoDocumento(preferencias) // desfaz o otimismo em caso de erro
        throw erro
      } finally {
        setSalvando(false)
      }
    },
    [preferencias, queryClient, usuario],
  )

  const falarTexto = useCallback(
    (texto: string) => {
      if (!suportaLeituraEmVoz || !preferencias.leitura_voz_alta) return
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(texto)
      utterance.lang = 'pt-BR'
      window.speechSynthesis.speak(utterance)
    },
    [preferencias.leitura_voz_alta, suportaLeituraEmVoz],
  )

  const pararFala = useCallback(() => {
    if (suportaLeituraEmVoz) window.speechSynthesis.cancel()
  }, [suportaLeituraEmVoz])

  const value = useMemo(
    () => ({ preferencias, salvando, salvarPreferencias, falarTexto, pararFala, suportaLeituraEmVoz }),
    [preferencias, salvando, salvarPreferencias, falarTexto, pararFala, suportaLeituraEmVoz],
  )

  return (
    <AccessibilityContext.Provider value={value}>{children}</AccessibilityContext.Provider>
  )
}
