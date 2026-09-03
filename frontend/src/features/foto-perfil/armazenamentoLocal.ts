/** Modo "só neste navegador": a foto nunca sai do dispositivo do usuário,
 * fica em base64 no localStorage. Mais privado que o upload pro servidor,
 * mas não aparece pra colegas nem em outro dispositivo/navegador. */

const PREFIXO = 'foto-perfil-local:'
const EVENTO_MUDANCA = 'foto-perfil-local:mudou'

export function salvarFotoLocal(usuarioId: string, dataUrl: string): void {
  try {
    localStorage.setItem(PREFIXO + usuarioId, dataUrl)
  } catch {
    // localStorage indisponível ou sem espaço - a foto simplesmente não
    // fica salva neste navegador, sem quebrar o resto da página.
  }
  window.dispatchEvent(new Event(EVENTO_MUDANCA))
}

export function obterFotoLocal(usuarioId: string): string | null {
  try {
    return localStorage.getItem(PREFIXO + usuarioId)
  } catch {
    return null
  }
}

export function removerFotoLocal(usuarioId: string): void {
  try {
    localStorage.removeItem(PREFIXO + usuarioId)
  } catch {
    // ignora
  }
  window.dispatchEvent(new Event(EVENTO_MUDANCA))
}

/** Notifica outros componentes montados (ex: avatar do menu lateral) quando
 * a foto local muda, já que localStorage não é reativo por conta própria. */
export function assinarMudancaFotoLocal(callback: () => void): () => void {
  window.addEventListener(EVENTO_MUDANCA, callback)
  return () => window.removeEventListener(EVENTO_MUDANCA, callback)
}

export function arquivoParaDataUrl(arquivo: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const leitor = new FileReader()
    leitor.onload = () => resolve(leitor.result as string)
    leitor.onerror = () => reject(leitor.error ?? new Error('Falha ao ler o arquivo.'))
    leitor.readAsDataURL(arquivo)
  })
}
