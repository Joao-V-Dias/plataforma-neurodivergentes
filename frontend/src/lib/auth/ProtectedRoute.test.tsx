import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AuthContext } from './AuthContext'
import { ProtectedRoute } from './ProtectedRoute'
import type { UsuarioPublico } from '@/lib/api/types'

const usuarioAluno: UsuarioPublico = {
  id: 'u1',
  nome: 'Aluno Teste',
  email: 'aluno@teste.com',
  papel: 'aluno',
  instituicao_id: 'i1',
  is_active: true,
  created_at: new Date().toISOString(),
}

function renderComAuth(usuario: UsuarioPublico | null, carregando: boolean, papelMinimo?: 'professor') {
  return render(
    <AuthContext.Provider
      value={{
        usuario,
        carregando,
        login: async () => usuarioAluno,
        logout: async () => {},
        atualizarUsuario: async () => {},
      }}
    >
      <MemoryRouter initialEntries={['/privado']}>
        <Routes>
          <Route path="/login" element={<p>Tela de login</p>} />
          <Route path="/nao-autorizado" element={<p>Não autorizado</p>} />
          <Route
            path="/privado"
            element={
              <ProtectedRoute papelMinimo={papelMinimo}>
                <p>Conteúdo protegido</p>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('ProtectedRoute', () => {
  it('mostra spinner enquanto carrega a sessão', () => {
    renderComAuth(null, true)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo protegido')).not.toBeInTheDocument()
  })

  it('redireciona para /login quando não autenticado', () => {
    renderComAuth(null, false)
    expect(screen.getByText('Tela de login')).toBeInTheDocument()
  })

  it('renderiza o conteúdo quando autenticado e sem restrição de papel', () => {
    renderComAuth(usuarioAluno, false)
    expect(screen.getByText('Conteúdo protegido')).toBeInTheDocument()
  })

  it('redireciona para /nao-autorizado quando o papel não atende o mínimo', () => {
    renderComAuth(usuarioAluno, false, 'professor')
    expect(screen.getByText('Não autorizado')).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo protegido')).not.toBeInTheDocument()
  })
})
