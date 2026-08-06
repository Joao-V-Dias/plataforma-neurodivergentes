import { lazy, Suspense, type ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { ProtectedRoute } from '@/lib/auth/ProtectedRoute'
import { PageSpinner } from '@/components/ui/Spinner'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { NaoAutorizadoPage } from '@/pages/NaoAutorizadoPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import type { Papel } from '@/lib/api/types'

// Code-split o resto das páginas: o editor de código (CodeMirror) e as
// primitivas Radix usadas nas telas de gestão são o grosso do bundle -
// nenhuma delas precisa estar no chunk inicial (tela de login).
const UsuariosListPage = lazy(() =>
  import('@/pages/usuarios/UsuariosListPage').then((m) => ({ default: m.UsuariosListPage })),
)
const MeuPerfilPage = lazy(() =>
  import('@/pages/perfil/MeuPerfilPage').then((m) => ({ default: m.MeuPerfilPage })),
)
const AcessibilidadePage = lazy(() =>
  import('@/pages/perfil/AcessibilidadePage').then((m) => ({ default: m.AcessibilidadePage })),
)
const TurmasPage = lazy(() =>
  import('@/pages/turmas/TurmasPage').then((m) => ({ default: m.TurmasPage })),
)
const TurmaDetalhePage = lazy(() =>
  import('@/pages/turmas/TurmaDetalhePage').then((m) => ({ default: m.TurmaDetalhePage })),
)
const ProblemasPage = lazy(() =>
  import('@/pages/problemas/ProblemasPage').then((m) => ({ default: m.ProblemasPage })),
)
const NovoProblemaPage = lazy(() =>
  import('@/pages/problemas/NovoProblemaPage').then((m) => ({ default: m.NovoProblemaPage })),
)
const ProblemaDetalhePage = lazy(() =>
  import('@/pages/problemas/ProblemaDetalhePage').then((m) => ({ default: m.ProblemaDetalhePage })),
)

function Protegida({ children, papelMinimo }: { children: ReactNode; papelMinimo?: Papel }) {
  return (
    <ProtectedRoute papelMinimo={papelMinimo}>
      <AppShell>
        <Suspense fallback={<PageSpinner />}>{children}</Suspense>
      </AppShell>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/cadastro" element={<RegisterPage />} />
      <Route path="/esqueci-senha" element={<ForgotPasswordPage />} />
      <Route path="/redefinir-senha" element={<ResetPasswordPage />} />

      <Route path="/" element={<Protegida><DashboardPage /></Protegida>} />
      <Route path="/turmas" element={<Protegida><TurmasPage /></Protegida>} />
      <Route
        path="/turmas/:turmaId"
        element={
          <Protegida papelMinimo="professor">
            <TurmaDetalhePage />
          </Protegida>
        }
      />
      <Route path="/problemas" element={<Protegida><ProblemasPage /></Protegida>} />
      <Route
        path="/problemas/novo"
        element={
          <Protegida papelMinimo="professor">
            <NovoProblemaPage />
          </Protegida>
        }
      />
      <Route path="/problemas/:problemaId" element={<Protegida><ProblemaDetalhePage /></Protegida>} />
      <Route
        path="/usuarios"
        element={
          <Protegida papelMinimo="professor">
            <UsuariosListPage />
          </Protegida>
        }
      />
      <Route path="/perfil" element={<Protegida><MeuPerfilPage /></Protegida>} />
      <Route path="/acessibilidade" element={<Protegida><AcessibilidadePage /></Protegida>} />

      <Route path="/nao-autorizado" element={<NaoAutorizadoPage />} />
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}
