import { isAxiosError } from 'axios'
import type { ErrorResponse } from './types'

/** Extrai a mensagem legível de um erro vindo do backend (envelope único
 * de app/schemas/error.py:ErrorResponse) - com um fallback genérico para
 * erros de rede ou respostas fora do formato esperado. */
export function mensagemDeErro(erro: unknown): string {
  if (isAxiosError<ErrorResponse>(erro)) {
    const mensagemApi = erro.response?.data?.error?.message
    if (mensagemApi) return mensagemApi
    if (erro.code === 'ERR_NETWORK') {
      return 'Não foi possível conectar ao servidor. Verifique sua conexão.'
    }
    if (erro.response?.status === 404) return 'Recurso não encontrado.'
  }
  if (erro instanceof Error) return erro.message
  return 'Ocorreu um erro inesperado.'
}

/** Erros de validação por campo (422), quando presentes - usado para
 * marcar campos individuais de formulário além da mensagem geral. */
export function erroPorCampo(erro: unknown): Record<string, string[]> | null {
  if (isAxiosError<ErrorResponse>(erro)) {
    return erro.response?.data?.error?.fields ?? null
  }
  return null
}
