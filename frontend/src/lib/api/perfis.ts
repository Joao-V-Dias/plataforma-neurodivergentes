import { isAxiosError } from 'axios'
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

export async function registrarPerfilAluno(
  alunoId: string,
  payload: RegistrarPerfilAlunoRequest,
): Promise<PerfilAlunoResponse> {
  const { data } = await apiClient.post<PerfilAlunoResponse>(
    `/alunos/${alunoId}/perfil`,
    payload,
  )
  return data
}

export async function obterPerfilAlunoVigente(
  alunoId: string,
): Promise<PerfilAlunoResponse | null> {
  try {
    const { data } = await apiClient.get<PerfilAlunoResponse>(`/alunos/${alunoId}/perfil`)
    return data
  } catch (erro) {
    if (isNotFound(erro)) return null
    throw erro
  }
}

export async function obterHistoricoPerfilAluno(alunoId: string): Promise<PerfilAlunoResponse[]> {
  const { data } = await apiClient.get<PerfilAlunoResponse[]>(
    `/alunos/${alunoId}/perfil/historico`,
  )
  return data
}

/** POST /me/big-five - sempre autoaplicado (o próprio usuário logado
 * responde por si, não existe rota para um Professor+ preencher em nome
 * de um aluno - ver app/api/v1/perfis.py:registrar_meu_big_five). */
export async function responderMeuBigFive(
  payload: BigFiveRespostasRequest,
): Promise<PerfilBigFiveResponse> {
  const { data } = await apiClient.post<PerfilBigFiveResponse>('/me/big-five', payload)
  return data
}

export async function obterBigFiveVigente(alunoId: string): Promise<PerfilBigFiveResponse | null> {
  try {
    const { data } = await apiClient.get<PerfilBigFiveResponse>(`/alunos/${alunoId}/big-five`)
    return data
  } catch (erro) {
    if (isNotFound(erro)) return null
    throw erro
  }
}

export async function obterMinhasPreferenciasAcessibilidade(): Promise<PreferenciasAcessibilidadeResponse> {
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

function isNotFound(erro: unknown): boolean {
  return isAxiosError(erro) && erro.response?.status === 404
}
