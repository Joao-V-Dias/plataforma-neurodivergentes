import { Ear } from 'lucide-react'
import { useState } from 'react'
import { Dialog } from '@/components/ui/Dialog'
import { CamposAcessibilidade } from './CamposAcessibilidade'

/** Painel de preferências de acessibilidade - deve estar a 1 clique do
 * header em toda a plataforma (docs/prompt-redesign-frontend.md §2.1). */
export function AcessibilidadePainel() {
  const [aberto, setAberto] = useState(false)

  return (
    <>
      <button
        type="button"
        className="a11y-trigger"
        onClick={() => setAberto(true)}
        aria-label="Preferências de acessibilidade"
      >
        <Ear size={18} />
      </button>
      <Dialog
        open={aberto}
        onOpenChange={setAberto}
        titulo="Acessibilidade"
        descricao="Ajustes salvos no seu perfil e aplicados em toda a plataforma."
      >
        <CamposAcessibilidade />
      </Dialog>
    </>
  )
}
