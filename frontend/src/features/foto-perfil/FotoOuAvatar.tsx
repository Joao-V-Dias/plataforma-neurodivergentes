import { Avatar } from '@/components/ui/Avatar'
import type { AvatarCodigo } from '@/lib/api/types'
import { useMinhaFotoUrl } from './useFotoPerfil'
import './FotoOuAvatar.css'

/** Mesmo lugar que o <Avatar> de ícone (menu lateral, perfil): mostra a
 * foto enviada pelo usuário quando existir, senão cai pro ícone. */
export function FotoOuAvatar({
  codigoAvatar,
  tamanho = 40,
}: {
  codigoAvatar: AvatarCodigo | null | undefined
  tamanho?: number
}) {
  const fotoUrl = useMinhaFotoUrl()

  if (fotoUrl) {
    return (
      <img
        className="foto-ou-avatar"
        src={fotoUrl}
        alt="Sua foto de perfil"
        style={{ width: tamanho, height: tamanho }}
      />
    )
  }

  return <Avatar codigo={codigoAvatar} tamanho={tamanho} />
}
