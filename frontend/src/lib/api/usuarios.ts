import { apiClient } from './client'
import type { CriarUsuarioRequest, UsuarioPublico } from './types'

export async function listarUsuarios(): Promise<UsuarioPublico[]> {
  const { data } = await apiClient.get<UsuarioPublico[]>('/usuarios')
  return data
}

export async function obterUsuario(id: string): Promise<UsuarioPublico> {
  const { data } = await apiClient.get<UsuarioPublico>(`/usuarios/${id}`)
  return data
}

export async function criarUsuario(payload: CriarUsuarioRequest): Promise<UsuarioPublico> {
  const { data } = await apiClient.post<UsuarioPublico>('/usuarios', payload)
  return data
}

export async function aprovarUsuario(id: string): Promise<UsuarioPublico> {
  const { data } = await apiClient.post<UsuarioPublico>(`/usuarios/${id}/aprovar`)
  return data
}
