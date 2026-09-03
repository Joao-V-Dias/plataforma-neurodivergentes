import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import './Button.css'

type Variante = 'primario' | 'secundario' | 'fantasma' | 'perigo'
type Tamanho = 'sm' | 'md'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  tamanho?: Tamanho
  carregando?: boolean
}

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variante = 'primario', tamanho = 'md', carregando, className, children, disabled, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cn('btn', `btn--${variante}`, `btn--${tamanho}`, carregando && 'btn--carregando', className)}
      disabled={disabled || carregando}
      aria-busy={carregando || undefined}
      {...props}
    >
      {children}
    </button>
  )
})
