import { apiClient } from './client'
import type {
  ForgotPasswordResponse,
  LoginRequest,
  RegistroAlunoRequest,
  TokenResponse,
  UsuarioPublico,
} from './types'

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', payload)
  return data
}

export async function registrar(payload: RegistroAlunoRequest): Promise<UsuarioPublico> {
  const { data } = await apiClient.post<UsuarioPublico>('/auth/register', payload)
  return data
}

export async function esqueciSenha(email: string): Promise<ForgotPasswordResponse> {
  const { data } = await apiClient.post<ForgotPasswordResponse>('/auth/forgot-password', { email })
  return data
}

export async function redefinirSenha(token: string, novaSenha: string): Promise<void> {
  await apiClient.post('/auth/reset-password', { token, nova_senha: novaSenha })
}

export async function logout(refreshToken: string): Promise<void> {
  await apiClient.post('/auth/logout', { refresh_token: refreshToken })
}

export async function obterMe(): Promise<UsuarioPublico> {
  const { data } = await apiClient.get<UsuarioPublico>('/auth/me')
  return data
}
