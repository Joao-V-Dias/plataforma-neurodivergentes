import { apiClient } from './client'
import type {
  EmblemaConquistadoResponse,
  EmblemaResponse,
  PerfilJogoRequest,
  PerfilJogoResponse,
  PontuacaoResponse,
} from './types'

export async function obterMeuAvatar(): Promise<PerfilJogoResponse> {
  const { data } = await apiClient.get<PerfilJogoResponse>('/me/avatar')
  return data
}

export async function atualizarMeuAvatar(payload: PerfilJogoRequest): Promise<PerfilJogoResponse> {
  const { data } = await apiClient.put<PerfilJogoResponse>('/me/avatar', payload)
  return data
}

export async function obterMinhaPontuacao(): Promise<PontuacaoResponse> {
  const { data } = await apiClient.get<PontuacaoResponse>('/me/pontuacao')
  return data
}

export async function obterPontuacaoDeAluno(alunoId: string): Promise<PontuacaoResponse> {
  const { data } = await apiClient.get<PontuacaoResponse>(`/alunos/${alunoId}/pontuacao`)
  return data
}

export async function listarEmblemas(): Promise<EmblemaResponse[]> {
  const { data } = await apiClient.get<EmblemaResponse[]>('/emblemas')
  return data
}

export async function listarMeusEmblemas(): Promise<EmblemaConquistadoResponse[]> {
  const { data } = await apiClient.get<EmblemaConquistadoResponse[]>('/me/emblemas')
  return data
}
