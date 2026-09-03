import { AxiosError } from 'axios'
import { apiClient } from '@/lib/api/client'

// --- app/foto_perfil/schemas.py -------------------------------------------
export interface FotoPerfilResponse {
  usuario_id: string
  url: string
}

export async function enviarFotoPerfilServidor(arquivo: File): Promise<FotoPerfilResponse> {
  const formData = new FormData()
  formData.append('arquivo', arquivo)
  const { data } = await apiClient.put<FotoPerfilResponse>('/me/foto', formData)
  return data
}

export async function obterMinhaFotoServidor(): Promise<FotoPerfilResponse | null> {
  try {
    const { data } = await apiClient.get<FotoPerfilResponse>('/me/foto')
    return data
  } catch (erro) {
    if (erro instanceof AxiosError && erro.response?.status === 404) return null
    throw erro
  }
}

export async function removerFotoPerfilServidor(): Promise<void> {
  await apiClient.delete('/me/foto')
}

/** Baixa o arquivo da foto como blob (não dá pra usar direto num <img src>
 * porque a rota exige o Bearer token do usuário logado). */
export async function baixarFotoDeUsuario(usuarioId: string): Promise<Blob> {
  const { data } = await apiClient.get<Blob>(`/usuarios/${usuarioId}/foto/arquivo`, {
    responseType: 'blob',
  })
  return data
}
