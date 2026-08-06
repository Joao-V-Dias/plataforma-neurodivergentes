/**
 * Persistência dos tokens JWT (access + refresh) em localStorage.
 *
 * Trade-off consciente: localStorage é vulnerável a exfiltração via XSS
 * (diferente de um cookie httpOnly). Optamos por ele porque este é um SPA
 * puro sem um backend-for-frontend próprio para setar cookies, e o
 * backend (Parte 2) já implementa rotação de refresh token com detecção
 * de reuso - um refresh token roubado e reutilizado após o legítimo já
 * ter girado invalida a família inteira do lado do servidor. Mitiga,
 * não elimina, o risco.
 */

const ACCESS_TOKEN_KEY = 'plataforma.access_token'
const REFRESH_TOKEN_KEY = 'plataforma.refresh_token'
const ACCESS_EXPIRES_KEY = 'plataforma.access_token_expires_at'

export interface TokenPair {
  accessToken: string
  refreshToken: string
  accessTokenExpiresAt: string
}

export function salvarTokens(tokens: TokenPair): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken)
  localStorage.setItem(ACCESS_EXPIRES_KEY, tokens.accessTokenExpiresAt)
}

export function obterAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function obterRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function limparTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(ACCESS_EXPIRES_KEY)
}

export function temSessaoPersistida(): boolean {
  return obterRefreshToken() !== null
}
