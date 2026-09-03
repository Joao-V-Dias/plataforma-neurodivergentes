import { lazy, Suspense, type ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AlunoShell } from '@/components/layout/AlunoShell'
import { GestaoShell } from '@/components/layout/GestaoShell'
import { PageSpinner } from '@/components/ui/Spinner'
import { AguardandoAprovacaoPage } from '@/pages/auth/AguardandoAprovacaoPage'
import { CadastroEnviadoPage } from '@/pages/auth/CadastroEnviadoPage'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage'
import { NaoAutorizadoPage } from '@/pages/NaoAutorizadoPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { ProtectedRoute } from '@/lib/auth/ProtectedRoute'
import { useAuth } from '@/lib/auth/useAuth'
import type { Papel } from '@/lib/api/types'

const OnboardingPage = lazy(() => import('@/pages/onboarding/OnboardingPage').then((m) => ({ default: m.OnboardingPage })))
const MinhasTurmasPage = lazy(() => import('@/pages/aluno/MinhasTurmasPage').then((m) => ({ default: m.MinhasTurmasPage })))
const MapaDoJogoPage = lazy(() => import('@/pages/aluno/MapaDoJogoPage').then((m) => ({ default: m.MapaDoJogoPage })))
const ProblemaPage = lazy(() => import('@/pages/problemas/ProblemaPage').then((m) => ({ default: m.ProblemaPage })))
const MeuProgressoPage = lazy(() => import('@/pages/aluno/MeuProgressoPage').then((m) => ({ default: m.MeuProgressoPage })))
const AgendaPage = lazy(() => import('@/pages/aluno/AgendaPage').then((m) => ({ default: m.AgendaPage })))
const BatalhaPage = lazy(() => import('@/pages/aluno/BatalhaPage').then((m) => ({ default: m.BatalhaPage })))
const PerfilPage = lazy(() => import('@/pages/aluno/PerfilPage').then((m) => ({ default: m.PerfilPage })))

const DashboardTurmasPage = lazy(() => import('@/pages/gestao/DashboardTurmasPage').then((m) => ({ default: m.DashboardTurmasPage })))
const TurmaDetalhePage = lazy(() => import('@/pages/gestao/TurmaDetalhePage').then((m) => ({ default: m.TurmaDetalhePage })))
const FilaAprovacaoPage = lazy(() => import('@/pages/gestao/FilaAprovacaoPage').then((m) => ({ default: m.FilaAprovacaoPage })))
const UsuariosPage = lazy(() => import('@/pages/gestao/UsuariosPage').then((m) => ({ default: m.UsuariosPage })))
const ProblemasBancoPage = lazy(() => import('@/pages/gestao/ProblemasBancoPage').then((m) => ({ default: m.ProblemasBancoPage })))
const NovoProblemaPage = lazy(() => import('@/pages/gestao/NovoProblemaPage').then((m) => ({ default: m.NovoProblemaPage })))
const ProblemaGestaoDetalhePage = lazy(() =>
  import('@/pages/gestao/ProblemaGestaoDetalhePage').then((m) => ({ default: m.ProblemaGestaoDetalhePage })),
)
const PainelDicasAlunoPage = lazy(() =>
  import('@/pages/gestao/PainelDicasAlunoPage').then((m) => ({ default: m.PainelDicasAlunoPage })),
)

function ProtegidaAluno({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <AlunoShell>
        <Suspense fallback={<PageSpinner />}>{children}</Suspense>
      </AlunoShell>
    </ProtectedRoute>
  )
}

function ProtegidaGestao({ children, papelMinimo }: { children: ReactNode; papelMinimo?: Papel }) {
  return (
    <ProtectedRoute papelMinimo={papelMinimo ?? 'professor'}>
      <GestaoShell>
        <Suspense fallback={<PageSpinner />}>{children}</Suspense>
      </GestaoShell>
    </ProtectedRoute>
  )
}

function Home() {
  const { usuario } = useAuth()
  if (usuario?.papel === 'aluno') {
    return (
      <ProtegidaAluno>
        <MinhasTurmasPage />
      </ProtegidaAluno>
    )
  }
  return <Navigate to="/gestao" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/cadastro" element={<RegisterPage />} />
      <Route path="/cadastro-enviado" element={<CadastroEnviadoPage />} />
      <Route path="/esqueci-senha" element={<ForgotPasswordPage />} />
      <Route path="/redefinir-senha" element={<ResetPasswordPage />} />
      <Route path="/aguardando-aprovacao" element={<AguardandoAprovacaoPage />} />

      <Route path="/" element={<Home />} />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <Suspense fallback={<PageSpinner />}>
              <OnboardingPage />
            </Suspense>
          </ProtectedRoute>
        }
      />
      <Route
        path="/turmas/:turmaId/mapa"
        element={
          <ProtegidaAluno>
            <MapaDoJogoPage />
          </ProtegidaAluno>
        }
      />
      <Route
        path="/turmas/:turmaId/problemas/:problemaId"
        element={
          <ProtegidaAluno>
            <ProblemaPage />
          </ProtegidaAluno>
        }
      />
      <Route
        path="/turmas/:turmaId/progresso"
        element={
          <ProtegidaAluno>
            <MeuProgressoPage />
          </ProtegidaAluno>
        }
      />
      <Route
        path="/agenda"
        element={
          <ProtegidaAluno>
            <AgendaPage />
          </ProtegidaAluno>
        }
      />
      <Route
        path="/batalha"
        element={
          <ProtegidaAluno>
            <BatalhaPage />
          </ProtegidaAluno>
        }
      />
      <Route
        path="/perfil"
        element={
          <ProtegidaAluno>
            <PerfilPage />
          </ProtegidaAluno>
        }
      />

      <Route
        path="/gestao"
        element={
          <ProtegidaGestao>
            <DashboardTurmasPage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/turmas/:turmaId"
        element={
          <ProtegidaGestao>
            <TurmaDetalhePage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/aprovacoes"
        element={
          <ProtegidaGestao>
            <FilaAprovacaoPage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/usuarios"
        element={
          <ProtegidaGestao>
            <UsuariosPage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/problemas"
        element={
          <ProtegidaGestao>
            <ProblemasBancoPage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/problemas/novo"
        element={
          <ProtegidaGestao>
            <NovoProblemaPage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/problemas/:problemaId"
        element={
          <ProtegidaGestao>
            <ProblemaGestaoDetalhePage />
          </ProtegidaGestao>
        }
      />
      <Route
        path="/gestao/problemas/:problemaId/dicas/:alunoId"
        element={
          <ProtegidaGestao>
            <PainelDicasAlunoPage />
          </ProtegidaGestao>
        }
      />

      <Route path="/nao-autorizado" element={<NaoAutorizadoPage />} />
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}
