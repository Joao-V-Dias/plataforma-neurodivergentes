import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import * as authApi from '@/lib/api/auth'
import {
  limparTokens,
  obterRefreshToken,
  salvarTokens,
  temSessaoPersistida,
} from '@/lib/api/tokenStorage'
import { registrarCallbackSessaoExpirada } from '@/lib/api/client'
import type { UsuarioPublico } from '@/lib/api/types'

interface AuthContextValue {
  usuario: UsuarioPublico | null
  carregando: boolean
  login: (email: string, senha: string) => Promise<UsuarioPublico>
  logout: () => Promise<void>
  /** Recarrega o usuário atual (ex: depois de mudar preferências que
   * afetam o próprio registro) sem exigir novo login. */
  atualizarUsuario: () => Promise<void>
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioPublico | null>(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    let ativo = true

    async function bootstrap() {
      if (!temSessaoPersistida()) {
        setCarregando(false)
        return
      }
      try {
        const atual = await authApi.obterUsuarioAtual()
        if (ativo) setUsuario(atual)
      } catch {
        limparTokens()
        if (ativo) setUsuario(null)
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void bootstrap()
    return () => {
      ativo = false
    }
  }, [])

  useEffect(() => {
    registrarCallbackSessaoExpirada(() => setUsuario(null))
  }, [])

  const login = useCallback(async (email: string, senha: string) => {
    const tokens = await authApi.login({ email, senha })
    salvarTokens({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      accessTokenExpiresAt: tokens.access_token_expires_at,
    })
    const atual = await authApi.obterUsuarioAtual()
    setUsuario(atual)
    return atual
  }, [])

  const logout = useCallback(async () => {
    const refreshToken = obterRefreshToken()
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken)
      } catch {
        // Best-effort: mesmo se a chamada falhar (ex: rede), a sessão
        // local é sempre encerrada.
      }
    }
    limparTokens()
    setUsuario(null)
  }, [])

  const atualizarUsuario = useCallback(async () => {
    const atual = await authApi.obterUsuarioAtual()
    setUsuario(atual)
  }, [])

  const value = useMemo(
    () => ({ usuario, carregando, login, logout, atualizarUsuario }),
    [usuario, carregando, login, logout, atualizarUsuario],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
