import { Volume2, VolumeX } from 'lucide-react'
import { useState } from 'react'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import { Button } from './Button'

/** Botão "ouvir" que lê um texto em voz alta (Web Speech API) - só
 * aparece quando o usuário ativou "leitura em voz alta" nas preferências
 * de acessibilidade (Parte 3) e o navegador suporta a API. Usado nos
 * enunciados de problema e no conteúdo das dicas (Parte 6), que tendem a
 * ser blocos longos de texto - ajuda especialmente alunos com dislexia. */
export function BotaoOuvir({ texto, rotulo }: { texto: string; rotulo: string }) {
  const { falarTexto, pararFala, preferencias, suportaLeituraEmVoz } = useAccessibility()
  const [falando, setFalando] = useState(false)

  if (!suportaLeituraEmVoz || !preferencias.leitura_voz_alta) return null

  function alternar() {
    if (falando) {
      pararFala()
      setFalando(false)
      return
    }
    falarTexto(texto)
    setFalando(true)
    const utterance = window.speechSynthesis
    const verificar = setInterval(() => {
      if (!utterance.speaking) {
        setFalando(false)
        clearInterval(verificar)
      }
    }, 300)
  }

  return (
    <Button type="button" variant="secondary" onClick={alternar} aria-pressed={falando}>
      {falando ? <VolumeX className="h-4 w-4" aria-hidden="true" /> : <Volume2 className="h-4 w-4" aria-hidden="true" />}
      {falando ? `Parar leitura de ${rotulo}` : `Ouvir ${rotulo}`}
    </Button>
  )
}
