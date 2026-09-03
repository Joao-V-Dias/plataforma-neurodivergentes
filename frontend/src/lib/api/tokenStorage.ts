const ACCESS_KEY = 'pna.access_token'
const REFRESH_KEY = 'pna.refresh_token'
const EXPIRES_KEY = 'pna.access_token_expires_at'

interface Tokens {
  accessToken: string
  refreshToken: string
  accessTokenExpiresAt: string
}

export function salvarTokens(tokens: Tokens): void {
  localStorage.setItem(ACCESS_KEY, tokens.accessToken)
  localStorage.setItem(REFRESH_KEY, tokens.refreshToken)
  localStorage.setItem(EXPIRES_KEY, tokens.accessTokenExpiresAt)
}

export function obterAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY)
}

export function obterRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY)
}

export function obterAccessTokenExpiresAt(): string | null {
  return localStorage.getItem(EXPIRES_KEY)
}

export function limparTokens(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(EXPIRES_KEY)
}
