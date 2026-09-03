import { apiClient } from './client'
import type {
  CriarProblemaRequest,
  ProblemaDetalheResponse,
  ProblemaResponse,
  SubmeterCodigoRequest,
  SubmissaoResponse,
  SubmissaoResumoResponse,
  TagPublica,
} from './types'

export async function listarTags(): Promise<TagPublica[]> {
  const { data } = await apiClient.get<TagPublica[]>('/tags')
  return data
}

export async function criarProblema(payload: CriarProblemaRequest): Promise<ProblemaResponse> {
  const { data } = await apiClient.post<ProblemaResponse>('/problemas', payload)
  return data
}

export async function listarProblemas(): Promise<ProblemaResponse[]> {
  const { data } = await apiClient.get<ProblemaResponse[]>('/problemas')
  return data
}

export async function listarProblemasDaTurma(turmaId: string): Promise<ProblemaResponse[]> {
  const { data } = await apiClient.get<ProblemaResponse[]>(`/turmas/${turmaId}/problemas`)
  return data
}

export async function obterProblema(id: string): Promise<ProblemaDetalheResponse> {
  const { data } = await apiClient.get<ProblemaDetalheResponse>(`/problemas/${id}`)
  return data
}

export async function vincularProblemaATurma(problemaId: string, turmaId: string): Promise<void> {
  await apiClient.post(`/problemas/${problemaId}/turmas`, { turma_id: turmaId })
}

export async function submeterCodigo(
  problemaId: string,
  payload: SubmeterCodigoRequest,
): Promise<SubmissaoResponse> {
  const { data } = await apiClient.post<SubmissaoResponse>(
    `/problemas/${problemaId}/submissoes`,
    payload,
  )
  return data
}

export async function listarMinhasSubmissoes(problemaId: string): Promise<SubmissaoResumoResponse[]> {
  const { data } = await apiClient.get<SubmissaoResumoResponse[]>(
    `/problemas/${problemaId}/minhas-submissoes`,
  )
  return data
}

export async function listarSubmissoesDoProblema(
  problemaId: string,
): Promise<SubmissaoResumoResponse[]> {
  const { data } = await apiClient.get<SubmissaoResumoResponse[]>(
    `/problemas/${problemaId}/submissoes`,
  )
  return data
}

export async function obterSubmissao(id: string): Promise<SubmissaoResponse> {
  const { data } = await apiClient.get<SubmissaoResponse>(`/submissoes/${id}`)
  return data
}
