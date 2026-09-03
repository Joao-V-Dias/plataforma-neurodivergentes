import type { ReactNode } from 'react'
import './OnboardingLayout.css'

const ETAPAS = ['Consentimento', 'Perfil', 'Estilo pessoal', 'Acessibilidade', 'Avatar']

export function OnboardingLayout({ etapa, children }: { etapa: number; children: ReactNode }) {
  return (
    <div className="onboarding">
      <div className="onboarding__card">
        <ol className="onboarding__trilha" aria-label="Etapas do cadastro de perfil">
          {ETAPAS.map((nome, i) => (
            <li
              key={nome}
              className="onboarding__etapa"
              data-estado={i === etapa ? 'atual' : i < etapa ? 'concluida' : 'pendente'}
            >
              <span className="onboarding__marcador">{i < etapa ? '✓' : i + 1}</span>
              <span className="onboarding__nome-etapa">{nome}</span>
            </li>
          ))}
        </ol>
        <div className="onboarding__conteudo">{children}</div>
      </div>
    </div>
  )
}
