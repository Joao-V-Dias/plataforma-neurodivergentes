import { AxiosError } from 'axios'
import type { ErrorResponse } from './types'

export type CodigoErroApi =
  | 'validation_error'
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'rate_limited'
  | 'service_unavailable'
  | 'unknown'

export interface ErroApi {
  status: number | null
  code: CodigoErroApi
  message: string
  fields: Record<string, string[]> | null
  requestId: string | null
}

function codigoPorStatus(status: number | undefined, codigoServidor: string | undefined): CodigoErroApi {
  if (codigoServidor === 'validation_error') return 'validation_error'
  switch (status) {
    case 400:
    case 422:
      return 'validation_error'
    case 401:
      return 'unauthorized'
    case 403:
      return 'forbidden'
    case 404:
      return 'not_found'
    case 409:
      return 'conflict'
    case 429:
      return 'rate_limited'
    case 503:
      return 'service_unavailable'
    default:
      return 'unknown'
  }
}

const MENSAGENS_PADRAO: Record<CodigoErroApi, string> = {
  validation_error: 'Alguns campos precisam de ajuste.',
  unauthorized: 'Sua sessão expirou. Entre novamente.',
  forbidden: 'Você não tem permissão para esta ação.',
  not_found: 'Não encontramos o que você procura.',
  conflict: 'Essa ação não pode ser concluída no momento.',
  rate_limited: 'Muitas tentativas seguidas. Aguarde um instante e tente de novo.',
  service_unavailable: 'Este recurso está indisponível agora. Tente novamente em instantes.',
  unknown: 'Algo deu errado. Tente novamente.',
}

export function paraErroApi(erro: unknown): ErroApi {
  if (erro instanceof AxiosError) {
    const status = erro.response?.status
    const payload = erro.response?.data as ErrorResponse | undefined
    const code = codigoPorStatus(status, payload?.error?.code)
    return {
      status: status ?? null,
      code,
      message: payload?.error?.message ?? MENSAGENS_PADRAO[code],
      fields: payload?.error?.fields ?? null,
      requestId: payload?.request_id ?? null,
    }
  }
  return {
    status: null,
    code: 'unknown',
    message: MENSAGENS_PADRAO.unknown,
    fields: null,
    requestId: null,
  }
}
