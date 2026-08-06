import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import {
  limparTokens,
  obterAccessToken,
  obterRefreshToken,
  salvarTokens,
} from './tokenStorage'
import type { TokenResponse } from './types'

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000/api/v1'

/** Chamado pelo AuthProvider quando a sessão não pode mais ser renovada
 * (refresh token ausente/expirado/revogado) - limpa o estado de auth e
 * manda o usuário de volta para o login. Indireção via callback em vez de
 * importar o router aqui, para o cliente HTTP não depender da árvore de
 * componentes React. */
let onSessaoExpirada: (() => void) | null = null
export function registrarCallbackSessaoExpirada(cb: () => void): void {
  onSessaoExpirada = cb
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Instância separada, sem interceptors, só para o próprio /auth/refresh -
// evita loop infinito (um 401 do refresh não pode tentar se auto-renovar).
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

// Dedupe: se várias requisições tomam 401 ao mesmo tempo (ex: um dashboard
// disparando 3 chamadas em paralelo com o access token vencido), só uma
// chamada de /auth/refresh deve sair - as outras esperam a mesma promise.
let refreshEmAndamento: Promise<string> | null = null

async function renovarAccessToken(): Promise<string> {
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
