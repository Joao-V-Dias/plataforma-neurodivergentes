import type { ReactElement } from 'react'
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuthContext } from './AuthContext'
import { RoleGate } from './RoleGate'
import type { UsuarioPublico } from '@/lib/api/types'

function usuario(papel: UsuarioPublico['papel']): UsuarioPublico {
  return {
    id: 'u1',
    nome: 'Teste',
    email: 'teste@teste.com',
    papel,
    instituicao_id: 'i1',
    is_active: true,
    created_at: new Date().toISOString(),
  }
}

function renderComPapel(papel: UsuarioPublico['papel'] | null, gate: ReactElement) {
  return render(
    <AuthContext.Provider
      value={{
        usuario: papel ? usuario(papel) : null,
        carregando: false,
        login: async () => usuario('aluno'),
        logout: async () => {},
        atualizarUsuario: async () => {},
      }}
    >
      {gate}
    </AuthContext.Provider>,
  )
}

describe('RoleGate', () => {
  it('esconde o conteúdo quando não há usuário logado', () => {
    renderComPapel(null, <RoleGate papelMinimo="professor">segredo</RoleGate>)
    expect(screen.queryByText('segredo')).not.toBeInTheDocument()
  })

  it('mostra o conteúdo quando o papel atende o mínimo hierárquico', () => {
    renderComPapel('diretor', <RoleGate papelMinimo="professor">segredo</RoleGate>)
    expect(screen.getByText('segredo')).toBeInTheDocument()
  })

  it('esconde o conteúdo quando o papel não atende o mínimo', () => {
    renderComPapel('aluno', <RoleGate papelMinimo="professor">segredo</RoleGate>)
    expect(screen.queryByText('segredo')).not.toBeInTheDocument()
  })

  it('respeita lista explícita de papéis permitidos', () => {
    renderComPapel('aluno', <RoleGate papeis={['aluno']}>só aluno</RoleGate>)
    expect(screen.getByText('só aluno')).toBeInTheDocument()
  })

  it('renderiza o fallback quando bloqueado', () => {
    renderComPapel('aluno', (
      <RoleGate papelMinimo="professor" fallback={<span>sem acesso</span>}>
        segredo
      </RoleGate>
    ))
    expect(screen.getByText('sem acesso')).toBeInTheDocument()
  })
})
