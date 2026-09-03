import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  atualizarPreferenciasAcessibilidade,
  obterPreferenciasAcessibilidade,
} from '@/lib/api/perfis'
import type { PreferenciasAcessibilidadeRequest, PreferenciasAcessibilidadeResponse } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'

export type Tema = 'escuro' | 'claro'

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
  tema: Tema
  carregando: boolean
  salvando: boolean
  atualizar: (patch: Partial<PreferenciasAcessibilidadeRequest>) => Promise<void>
  alternarTema: () => void
}

// eslint-disable-next-line react-refresh/only-export-components
export const AccessibilityContext = createContext<AccessibilityContextValue | null>(null)

function aplicarAoDocumento(prefs: PreferenciasAcessibilidadeRequest, tema: Tema) {
  const root = document.documentElement
  root.dataset.theme = tema === 'claro' ? 'light' : 'dark'
  root.dataset.fonte = prefs.tamanho_fonte
  root.dataset.fonteLegivel = String(prefs.fonte_legivel)
  root.dataset.contraste = prefs.alto_contraste ? 'alto' : 'normal'
  root.dataset.reduzirEstimulos = String(prefs.reducao_estimulos)
}

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const { usuario } = useAuth()
  const [preferencias, setPreferencias] = useState<PreferenciasAcessibilidadeRequest>(PADRAO)
  const [tema, setTema] = useState<Tema>(() => {
    const salvo = localStorage.getItem('pna.tema')
    return salvo === 'escuro' ? 'escuro' : 'claro'
  })
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)

  useEffect(() => {
    aplicarAoDocumento(preferencias, tema)
  }, [preferencias, tema])

  useEffect(() => {
    if (!usuario) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- reset síncrono ao deslogar, não busca assíncrona
      setPreferencias(PADRAO)
      setCarregando(false)
      return
    }
    let cancelado = false
    setCarregando(true)
    obterPreferenciasAcessibilidade()
      .then((resp: PreferenciasAcessibilidadeResponse) => {
        if (!cancelado) setPreferencias(resp)
      })
      .catch(() => {
        if (!cancelado) setPreferencias(PADRAO)
      })
      .finally(() => {
        if (!cancelado) setCarregando(false)
      })
    return () => {
      cancelado = true
    }
  }, [usuario])

  const atualizar = useCallback(
    async (patch: Partial<PreferenciasAcessibilidadeRequest>) => {
      const proximo = { ...preferencias, ...patch }
      setPreferencias(proximo)
      if (!usuario) return
      setSalvando(true)
      try {
        const resp = await atualizarPreferenciasAcessibilidade(proximo)
        setPreferencias(resp)
      } finally {
        setSalvando(false)
      }
    },
    [preferencias, usuario],
  )

  const alternarTema = useCallback(() => {
    setTema((atual) => {
      const proximo = atual === 'escuro' ? 'claro' : 'escuro'
      localStorage.setItem('pna.tema', proximo)
      return proximo
    })
  }, [])

  const value = useMemo<AccessibilityContextValue>(
    () => ({ preferencias, tema, carregando, salvando, atualizar, alternarTema }),
    [preferencias, tema, carregando, salvando, atualizar, alternarTema],
  )

  return <AccessibilityContext.Provider value={value}>{children}</AccessibilityContext.Provider>
}
