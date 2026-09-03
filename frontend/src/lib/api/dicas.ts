import { apiClient } from './client'
import type { DicaComEficaciaResponse, DicaResponse } from './types'

export async function pedirDica(problemaId: string): Promise<DicaResponse> {
  const { data } = await apiClient.post<DicaResponse>(`/problemas/${problemaId}/dicas`)
  return data
}

export async function listarMinhasDicas(problemaId: string): Promise<DicaResponse[]> {
  const { data } = await apiClient.get<DicaResponse[]>(`/problemas/${problemaId}/minhas-dicas`)
  return data
}

export async function listarDicasDeAluno(
  problemaId: string,
  alunoId: string,
): Promise<DicaComEficaciaResponse[]> {
  const { data } = await apiClient.get<DicaComEficaciaResponse[]>(
    `/problemas/${problemaId}/dicas/${alunoId}`,
  )
  return data
}
