import { apiClient } from './client'
import type {
  BigFiveRespostasRequest,
  CondicaoPublica,
  PerfilAlunoResponse,
  PerfilBigFiveResponse,
  PreferenciasAcessibilidadeRequest,
  PreferenciasAcessibilidadeResponse,
  QuestaoTIPI,
  RegistrarPerfilAlunoRequest,
} from './types'

export async function listarCondicoes(): Promise<CondicaoPublica[]> {
  const { data } = await apiClient.get<CondicaoPublica[]>('/condicoes-neurodivergencia')
  return data
}

export async function obterQuestionarioBigFive(): Promise<QuestaoTIPI[]> {
  const { data } = await apiClient.get<QuestaoTIPI[]>('/big-five/questionario')
  return data
}

export async function enviarBigFive(payload: BigFiveRespostasRequest): Promise<PerfilBigFiveResponse> {
  const { data } = await apiClient.post<PerfilBigFiveResponse>('/me/big-five', payload)
  return data
}

export async function obterPreferenciasAcessibilidade(): Promise<PreferenciasAcessibilidadeResponse> {
  const { data } = await apiClient.get<PreferenciasAcessibilidadeResponse>(
    '/me/preferencias-acessibilidade',
  )
  return data
}

export async function atualizarPreferenciasAcessibilidade(
  payload: PreferenciasAcessibilidadeRequest,
): Promise<PreferenciasAcessibilidadeResponse> {
  const { data } = await apiClient.put<PreferenciasAcessibilidadeResponse>(
    '/me/preferencias-acessibilidade',
    payload,
  )
  return data
}

export async function registrarPerfilAluno(
  alunoId: string,
  payload: RegistrarPerfilAlunoRequest,
): Promise<PerfilAlunoResponse> {
  const { data } = await apiClient.post<PerfilAlunoResponse>(`/alunos/${alunoId}/perfil`, payload)
  return data
}

export async function obterPerfilAluno(alunoId: string): Promise<PerfilAlunoResponse> {
  const { data } = await apiClient.get<PerfilAlunoResponse>(`/alunos/${alunoId}/perfil`)
  return data
}

export async function obterHistoricoPerfilAluno(alunoId: string): Promise<PerfilAlunoResponse[]> {
  const { data } = await apiClient.get<PerfilAlunoResponse[]>(`/alunos/${alunoId}/perfil/historico`)
  return data
}

export async function obterBigFiveDeAluno(alunoId: string): Promise<PerfilBigFiveResponse> {
  const { data } = await apiClient.get<PerfilBigFiveResponse>(`/alunos/${alunoId}/big-five`)
  return data
}
