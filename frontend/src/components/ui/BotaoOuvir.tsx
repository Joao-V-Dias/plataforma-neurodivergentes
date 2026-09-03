import { useEffect, useState } from 'react'
import { Volume2, VolumeX } from 'lucide-react'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import './BotaoOuvir.css'

/** Lê `texto` em voz alta via Web Speech API. Só aparece quando a
 * preferência leitura_voz_alta está ligada (PreferenciasAcessibilidade) -
 * ver docs/prompt-redesign-frontend.md secção 2.1. */
export function BotaoOuvir({ texto }: { texto: string }) {
  const { preferencias } = useAccessibility()
  const [falando, setFalando] = useState(false)

  useEffect(() => {
    return () => window.speechSynthesis?.cancel()
  }, [])

  if (!preferencias.leitura_voz_alta || !('speechSynthesis' in window)) return null

  function alternar() {
    if (falando) {
      window.speechSynthesis.cancel()
      setFalando(false)
      return
    }
    const utterance = new SpeechSynthesisUtterance(texto)
    utterance.lang = 'pt-BR'
    utterance.onend = () => setFalando(false)
    utterance.onerror = () => setFalando(false)
    window.speechSynthesis.speak(utterance)
    setFalando(true)
  }

  return (
    <button
      type="button"
      className="botao-ouvir"
      onClick={alternar}
      aria-pressed={falando}
      aria-label={falando ? 'Parar leitura em voz alta' : 'Ouvir este texto'}
    >
      {falando ? <VolumeX size={14} /> : <Volume2 size={14} />}
      {falando ? 'Parar' : 'Ouvir'}
    </button>
  )
}
