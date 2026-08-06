import { apiClient } from './client'
import type {
  CriarTurmaRequest,
  MatriculaResponse,
  ProgressoAlunoResponse,
  TurmaDetalheResponse,
  TurmaResponse,
} from './types'

export async function listarTurmas(): Promise<TurmaResponse[]> {
  const { data } = await apiClient.get<TurmaResponse[]>('/turmas')
  return data
}

export async function criarTurma(payload: CriarTurmaRequest): Promise<TurmaResponse> {
  const { data } = await apiClient.post<TurmaResponse>('/turmas', payload)
  return data
}

export async function obterTurma(id: string): Promise<TurmaDetalheResponse> {
  const { data } = await apiClient.get<TurmaDetalheResponse>(`/turmas/${id}`)
  return data
}

export async function adicionarProfessor(turmaId: string, professorId: string): Promise<void> {
  await apiClient.post(`/turmas/${turmaId}/professores`, { professor_id: professorId })
}

export async function matricularAluno(turmaId: string, alunoId: string): Promise<MatriculaResponse> {
  const { data } = await apiClient.post<MatriculaResponse>(`/turmas/${turmaId}/matriculas`, {
    aluno_id: alunoId,
  })
  return data
}

export async function desmatricularAluno(turmaId: string, alunoId: string): Promise<void> {
  await apiClient.delete(`/turmas/${turmaId}/matriculas/${alunoId}`)
}

export async function listarMatriculas(turmaId: string): Promise<MatriculaResponse[]> {
  const { data } = await apiClient.get<MatriculaResponse[]>(`/turmas/${turmaId}/matriculas`)
  return data
}

export async function obterProgressoTurma(turmaId: string): Promise<ProgressoAlunoResponse[]> {
  const { data } = await apiClient.get<ProgressoAlunoResponse[]>(`/turmas/${turmaId}/progresso`)
  return data
}

export async function listarMinhasTurmas(): Promise<TurmaResponse[]> {
  const { data } = await apiClient.get<TurmaResponse[]>('/me/turmas')
  return data
}

export async function obterMeuProgresso(turmaId: string): Promise<ProgressoAlunoResponse> {
  const { data } = await apiClient.get<ProgressoAlunoResponse>(
    `/me/turmas/${turmaId}/progresso`,
  )
  return data
}
