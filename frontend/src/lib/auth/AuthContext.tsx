import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { obterMe, login as loginRequest, logout as logoutRequest } from '@/lib/api/auth'
import { registrarCallbackSessaoExpirada } from '@/lib/api/client'
import { limparTokens, obterAccessToken, obterRefreshToken, salvarTokens } from '@/lib/api/tokenStorage'
import type { LoginRequest, UsuarioPublico } from '@/lib/api/types'

interface AuthContextValue {
  usuario: UsuarioPublico | null
  carregando: boolean
  entrar: (payload: LoginRequest) => Promise<UsuarioPublico>
  sair: () => Promise<void>
  recarregarUsuario: () => Promise<void>
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioPublico | null>(null)
  const [carregando, setCarregando] = useState(true)

  const carregarUsuario = useCallback(async () => {
    if (!obterAccessToken()) {
      setUsuario(null)
      setCarregando(false)
      return
    }
    try {
      const me = await obterMe()
      setUsuario(me)
    } catch {
      limparTokens()
      setUsuario(null)
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    // Bootstrap de sessão a partir do token salvo - roda uma vez ao montar,
    // fora do fluxo de dados do react-query (que ainda não existe aqui em
    // cima da árvore de providers).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void carregarUsuario()
    registrarCallbackSessaoExpirada(() => {
      setUsuario(null)
    })
  }, [carregarUsuario])

  const entrar = useCallback(async (payload: LoginRequest) => {
    const tokens = await loginRequest(payload)
    salvarTokens({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      accessTokenExpiresAt: tokens.access_token_expires_at,
    })
    const me = await obterMe()
    setUsuario(me)
    return me
  }, [])

  const sair = useCallback(async () => {
    const refreshToken = obterRefreshToken()
    try {
      if (refreshToken) await logoutRequest(refreshToken)
    } catch {
      // segue o fluxo mesmo se a chamada de logout falhar - o token local
      // é limpo de qualquer forma.
    }
    limparTokens()
    setUsuario(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ usuario, carregando, entrar, sair, recarregarUsuario: carregarUsuario }),
    [usuario, carregando, entrar, sair, carregarUsuario],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
