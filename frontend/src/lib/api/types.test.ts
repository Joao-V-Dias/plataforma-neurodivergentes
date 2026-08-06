import { describe, expect, it } from 'vitest'
import { papeisCriaveisPor, papelAtendeMinimo } from './types'

describe('papeisCriaveisPor', () => {
  it('diretor pode criar todos os papeis abaixo', () => {
    expect(papeisCriaveisPor('diretor')).toEqual(['coordenador', 'professor', 'aluno'])
  })

  it('professor so pode criar aluno', () => {
    expect(papeisCriaveisPor('professor')).toEqual(['aluno'])
  })

  it('aluno nao pode criar ninguem', () => {
    expect(papeisCriaveisPor('aluno')).toEqual([])
  })
})

describe('papelAtendeMinimo', () => {
  it('diretor atende minimo professor', () => {
    expect(papelAtendeMinimo('diretor', 'professor')).toBe(true)
  })

  it('aluno nao atende minimo professor', () => {
    expect(papelAtendeMinimo('aluno', 'professor')).toBe(false)
  })

  it('papel atende a si mesmo como minimo', () => {
    expect(papelAtendeMinimo('professor', 'professor')).toBe(true)
  })
})
