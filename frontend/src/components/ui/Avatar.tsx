import { Bird, Cat, PawPrint, Squirrel, Turtle } from 'lucide-react'
import type { AvatarCodigo } from '@/lib/api/types'
import { cn } from '@/lib/cn'
import './Avatar.css'

const ICONE: Record<AvatarCodigo, typeof Cat> = {
  raposa: PawPrint,
  coruja: Bird,
  gato: Cat,
  passaro: Bird,
  urso: PawPrint,
  lobo: PawPrint,
  tartaruga: Turtle,
  esquilo: Squirrel,
}

const TOM: Record<AvatarCodigo, string> = {
  raposa: 'orange',
  coruja: 'accent',
  gato: 'pink',
  passaro: 'cyan',
  urso: 'yellow',
  lobo: 'muted',
  tartaruga: 'green',
  esquilo: 'orange',
}

export function Avatar({
  codigo,
  tamanho = 40,
}: {
  codigo: AvatarCodigo | null | undefined
  tamanho?: number
}) {
  const Icone = codigo ? ICONE[codigo] : PawPrint
  const tom = codigo ? TOM[codigo] : 'muted'
  return (
    <span
      className={cn('avatar', `avatar--${tom}`)}
      style={{ width: tamanho, height: tamanho }}
      aria-hidden="true"
    >
      <Icone size={tamanho * 0.55} strokeWidth={1.8} />
    </span>
  )
}
