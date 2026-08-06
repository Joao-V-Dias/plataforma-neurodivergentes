import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LoginPage } from './LoginPage'
import { AuthProvider } from '@/lib/auth/AuthContext'
import * as authApi from '@/lib/api/auth'
import type { UsuarioPublico } from '@/lib/api/types'

vi.mock('@/lib/api/auth')

const usuario: UsuarioPublico = {
  id: 'u1',
  nome: 'Aluno Teste',
  email: 'aluno@teste.com',
  papel: 'aluno',
  instituicao_id: 'i1',
  is_active: true,
  created_at: new Date().toISOString(),
}

function renderLoginPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<p>Painel principal</p>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LoginPage', () => {
  it('mostra erros de validação quando o formulário está vazio', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Informe um e-mail válido.')).toBeInTheDocument()
    expect(authApi.login).not.toHaveBeenCalled()
  })

  it('faz login e navega para a página inicial em caso de sucesso', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'access',
      access_token_expires_at: new Date().toISOString(),
      refresh_token: 'refresh',
      refresh_token_expires_at: new Date().toISOString(),
      token_type: 'bearer',
    })
    vi.mocked(authApi.obterUsuarioAtual).mockResolvedValue(usuario)

    const user = userEvent.setup()
    renderLoginPage()

    await user.type(screen.getByLabelText('E-mail'), 'aluno@teste.com')
    await user.type(screen.getByLabelText('Senha'), 'SenhaValida123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => expect(screen.getByText('Painel principal')).toBeInTheDocument())
    expect(authApi.login).toHaveBeenCalledWith({ email: 'aluno@teste.com', senha: 'SenhaValida123' })
  })

  it('mostra a mensagem de erro do backend em caso de credenciais inválidas', async () => {
    vi.mocked(authApi.login).mockRejectedValue({
      isAxiosError: true,
      response: { data: { error: { message: 'Credenciais inválidas.' } } },
    })

    const user = userEvent.setup()
    renderLoginPage()

    await user.type(screen.getByLabelText('E-mail'), 'aluno@teste.com')
    await user.type(screen.getByLabelText('Senha'), 'senhaerrada')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Credenciais inválidas.')).toBeInTheDocument()
  })
})
