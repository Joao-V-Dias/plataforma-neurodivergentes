import { useQuery } from '@tanstack/react-query'
import { Flame, LogOut, Map, NotebookPen, Swords, Trophy } from 'lucide-react'
import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { AcessibilidadePainel } from './AcessibilidadePainel'
import { FotoOuAvatar } from '@/features/foto-perfil/FotoOuAvatar'
import { obterMeuAvatar, obterMinhaPontuacao } from '@/lib/api/gamificacao'
import { useAuth } from '@/lib/auth/useAuth'
import { cn } from '@/lib/cn'
import './AlunoShell.css'

export function AlunoShell({ children }: { children: ReactNode }) {
  const { usuario, sair } = useAuth()
  const { data: pontuacao } = useQuery({ queryKey: ['minha-pontuacao'], queryFn: obterMinhaPontuacao })
  const { data: perfilJogo } = useQuery({ queryKey: ['meu-avatar'], queryFn: obterMeuAvatar })

  return (
    <div className="aluno-shell">
      <a className="skip-link" href="#conteudo">
        Pular para o conteúdo
      </a>

      <nav className="aluno-shell__trilho" aria-label="Navegação principal">
        <NavLink to="/" end className="aluno-shell__marca" aria-label="Plataforma Adaptativa">
          <span aria-hidden="true">{'</>'}</span>
        </NavLink>

        <ShellTab to="/" fim tom="turmas" icone={<Map size={17} />} texto="Turmas" />
        <ShellTab to="/agenda" tom="agenda" icone={<NotebookPen size={17} />} texto="Agenda" />
        <ShellTab to="/batalha" tom="batalha" icone={<Swords size={17} />} texto="Batalha" />

        <div className="aluno-shell__trilho-rodape">
          <AcessibilidadePainel />
          <NavLink to="/perfil" className="aluno-shell__perfil" title={usuario?.nome} aria-label="Meu perfil">
            <FotoOuAvatar codigoAvatar={perfilJogo?.avatar_codigo} tamanho={30} />
          </NavLink>
          <button type="button" className="aluno-shell__sair" onClick={() => void sair()} aria-label="Sair da conta">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="aluno-shell__corpo">
        <header className="aluno-shell__cabecalho">
          <span className="aluno-shell__cabecalho-nome">{usuario?.nome}</span>
          {pontuacao && (
            <div className="aluno-shell__marcacoes">
              <span className="aluno-shell__marcacao" title="Sequência de dias ativos">
                <Flame size={14} className="aluno-shell__icone-fogo" aria-hidden="true" />
                {pontuacao.sequencia_dias} dias seguidos
              </span>
              <span className="aluno-shell__marcacao" title="Pontos acumulados">
                <Trophy size={14} className="aluno-shell__icone-trofeu" aria-hidden="true" />
                {pontuacao.pontos} pts
              </span>
            </div>
          )}
        </header>
        <main id="conteudo" className="aluno-shell__conteudo">
          {children}
        </main>
      </div>
    </div>
  )
}

function ShellTab({
  to,
  icone,
  texto,
  fim,
  tom,
}: {
  to: string
  icone: ReactNode
  texto: string
  fim?: boolean
  tom: 'turmas' | 'agenda' | 'batalha'
}) {
  return (
    <NavLink
      to={to}
      end={fim}
      className={({ isActive }) => cn('aluno-shell__aba', `aluno-shell__aba--${tom}`, isActive && 'is-ativa')}
    >
      {icone}
      <span>{texto}</span>
    </NavLink>
  )
}
