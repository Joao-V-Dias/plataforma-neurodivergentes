import { AxiosError } from 'axios'
import { describe, expect, it } from 'vitest'
import { erroPorCampo, mensagemDeErro } from './errors'

function criarAxiosError(status: number, data: unknown): AxiosError {
  const erro = new AxiosError('Request failed', String(status))
  erro.response = {
    status,
    data,
    statusText: '',
    headers: {},
    // @ts-expect-error - config completo não é necessário para o teste
    config: {},
  }
  return erro
}

describe('mensagemDeErro', () => {
  it('extrai a mensagem do envelope de erro da API', () => {
    const erro = criarAxiosError(400, { error: { code: 'validation_error', message: 'Campo inválido.' } })
    expect(mensagemDeErro(erro)).toBe('Campo inválido.')
  })

  it('usa mensagem genérica de 404 quando não há mensagem no corpo', () => {
    const erro = criarAxiosError(404, {})
    expect(mensagemDeErro(erro)).toBe('Recurso não encontrado.')
  })

  it('usa mensagem de rede quando a requisição falha por conexão', () => {
    const erro = new AxiosError('Network Error')
    erro.code = 'ERR_NETWORK'
    expect(mensagemDeErro(erro)).toMatch(/conectar ao servidor/)
  })

  it('cai no fallback genérico para erros desconhecidos', () => {
    expect(mensagemDeErro('algo estranho')).toBe('Ocorreu um erro inesperado.')
  })
})

describe('erroPorCampo', () => {
  it('extrai os erros de campo do envelope 422', () => {
    const erro = criarAxiosError(422, {
      error: { code: 'validation_error', message: 'x', fields: { email: ['Email inválido.'] } },
    })
    expect(erroPorCampo(erro)).toEqual({ email: ['Email inválido.'] })
  })

  it('retorna null quando não é um erro da API', () => {
    expect(erroPorCampo(new Error('boom'))).toBeNull()
  })
})
