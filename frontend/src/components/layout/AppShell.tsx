import type { ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  BookOpen,
  LayoutDashboard,
  LogOut,
  School,
  Settings,
  UserCircle,
  Users,
} from 'lucide-react'
import { useAuth } from '@/lib/auth/useAuth'
import { PAPEL_LABEL, papelAtendeMinimo } from '@/lib/api/types'
import { cn } from '@/lib/cn'
import { useToast } from '@/components/ui/useToast'

interface NavItem {
  to: string
  label: string
  icon: typeof LayoutDashboard
  papelMinimo?: 'coordenador' | 'professor'
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Início', icon: LayoutDashboard },
  { to: '/turmas', label: 'Turmas', icon: School },
  { to: '/problemas', label: 'Problemas', icon: BookOpen },
  { to: '/usuarios', label: 'Usuários', icon: Users, papelMinimo: 'professor' },
  { to: '/perfil', label: 'Meu perfil', icon: UserCircle },
  { to: '/acessibilidade', label: 'Acessibilidade', icon: Settings },
]

export function AppShell({ children }: { children: ReactNode }) {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const { notificar } = useToast()

  if (!usuario) return <>{children}</>

  async function handleLogout() {
    await logout()
    notificar({ titulo: 'Sessão encerrada', tone: 'info' })
    navigate('/login', { replace: true })
  }

  const itensVisiveis = NAV_ITEMS.filter(
    (item) => !item.papelMinimo || papelAtendeMinimo(usuario.papel, item.papelMinimo),
  )

  return (
    <div className="flex min-h-screen flex-col">
      <a href="#conteudo-principal" className="skip-link">
        Pular para o conteúdo principal
      </a>

      <header data-card className="bg-[var(--color-bg)] shadow-[0_1px_2px_rgba(20,20,40,0.06)]">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <span className="text-base font-semibold text-[var(--color-primary)]">
            Plataforma Adaptativa
          </span>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-[var(--color-muted)]">
              {usuario.nome} · {PAPEL_LABEL[usuario.papel]}
            </span>
            <button
              type="button"
              onClick={() => void handleLogout()}
              className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[var(--color-fg)] hover:bg-[var(--color-surface)]"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
              Sair
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-8 px-6 py-8">
        <nav aria-label="Navegação principal" className="w-52 shrink-0">
          <ul className="flex flex-col gap-0.5">
            {itensVisiveis.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'
                        : 'text-[var(--color-muted)] hover:bg-[var(--color-surface)] hover:text-[var(--color-fg)]',
                    )
                  }
                >
                  <item.icon className="h-4 w-4" aria-hidden="true" />
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <main id="conteudo-principal" tabIndex={-1} className="min-w-0 flex-1 focus:outline-none">
          {children}
        </main>
      </div>
    </div>
  )
}
