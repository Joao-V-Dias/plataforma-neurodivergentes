import { ClipboardList, LayoutGrid, LogOut, UserCheck, Users } from 'lucide-react'
import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { AcessibilidadePainel } from './AcessibilidadePainel'
import { PAPEL_LABEL } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'
import { cn } from '@/lib/cn'
import './GestaoShell.css'

export function GestaoShell({ children }: { children: ReactNode }) {
  const { usuario, sair } = useAuth()

  return (
    <div className="gestao-shell">
      <a className="skip-link" href="#conteudo-gestao">
        Pular para o conteúdo
      </a>
      <aside className="gestao-shell__sidebar">
        <div className="gestao-shell__marca">
          <span className="gestao-shell__logo" aria-hidden="true">
            {'</>'}
          </span>
          <span>Gestão</span>
        </div>
        <nav className="gestao-shell__nav" aria-label="Navegação de gestão">
          <SidebarLink to="/gestao" fim icone={<LayoutGrid size={16} />} texto="Turmas" />
          <SidebarLink to="/gestao/aprovacoes" icone={<UserCheck size={16} />} texto="Aprovações" />
          <SidebarLink to="/gestao/usuarios" icone={<Users size={16} />} texto="Usuários" />
          <SidebarLink to="/gestao/problemas" icone={<ClipboardList size={16} />} texto="Banco de problemas" />
        </nav>
        <div className="gestao-shell__rodape">
          <AcessibilidadePainel />
          <div className="gestao-shell__usuario">
            <span className="gestao-shell__nome">{usuario?.nome}</span>
            <span className="gestao-shell__papel">{usuario ? PAPEL_LABEL[usuario.papel] : ''}</span>
          </div>
          <button type="button" className="gestao-shell__sair" onClick={() => void sair()} aria-label="Sair da conta">
            <LogOut size={16} />
          </button>
        </div>
      </aside>
      <main id="conteudo-gestao" className="gestao-shell__conteudo">
        {children}
      </main>
    </div>
  )
}

function SidebarLink({
  to,
  icone,
  texto,
  fim,
}: {
  to: string
  icone: ReactNode
  texto: string
  fim?: boolean
}) {
  return (
    <NavLink to={to} end={fim} className={({ isActive }) => cn('gestao-shell__link', isActive && 'is-ativo')}>
      {icone}
      {texto}
    </NavLink>
  )
}
