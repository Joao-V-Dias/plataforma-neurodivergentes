import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import {
  limparTokens,
  obterAccessToken,
  obterAccessTokenExpiresAt,
  obterRefreshToken,
  salvarTokens,
} from './tokenStorage'
import type { TokenResponse } from './types'

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000/api/v1'

let onSessaoExpirada: (() => void) | null = null
export function registrarCallbackSessaoExpirada(cb: () => void): void {
  onSessaoExpirada = cb
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Instância separada, sem interceptors, só para /auth/refresh - evita loop
// infinito (um 401 do próprio refresh não pode tentar se auto-renovar).
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = obterAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Dedupe: se várias chamadas tomam 401 ao mesmo tempo, só uma renovação sai.
let refreshEmAndamento: Promise<string> | null = null

export async function renovarAccessToken(): Promise<string> {
  if (refreshEmAndamento) return refreshEmAndamento

  const refreshToken = obterRefreshToken()
  if (!refreshToken) {
    throw new Error('Sem refresh token disponível.')
  }

  refreshEmAndamento = refreshClient
    .post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
    .then((resp) => {
      salvarTokens({
        accessToken: resp.data.access_token,
        refreshToken: resp.data.refresh_token,
        accessTokenExpiresAt: resp.data.access_token_expires_at,
      })
      return resp.data.access_token
    })
    .finally(() => {
      refreshEmAndamento = null
    })

  return refreshEmAndamento
}

/** Garante um access token com folga de validade antes de um uso que não
 * passa pelo interceptor de 401 do apiClient (ex: handshake de WebSocket,
 * que não tem como reagir a uma rejeição e tentar de novo). Renova
 * proativamente se faltar pouco (ou já tiver expirado); retorna null se não
 * houver sessão ou a renovação falhar. */
export async function garantirAccessTokenValido(): Promise<string | null> {
  const token = obterAccessToken()
  if (!token) return null

  const expiraEm = obterAccessTokenExpiresAt()
  const folgaMs = 15_000
  if (expiraEm && new Date(expiraEm).getTime() - Date.now() > folgaMs) {
    return token
  }

  try {
    return await renovarAccessToken()
  } catch {
    return null
  }
}

interface RequisicaoComRetry extends InternalAxiosRequestConfig {
  _retry?: boolean
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RequisicaoComRetry | undefined
    const isAuthEndpoint = original?.url?.startsWith('/auth/')

    if (error.response?.status === 401 && original && !original._retry && !isAuthEndpoint) {
      original._retry = true
      try {
        const novoToken = await renovarAccessToken()
        original.headers.Authorization = `Bearer ${novoToken}`
        return apiClient(original)
      } catch {
        limparTokens()
        onSessaoExpirada?.()
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  },
)
