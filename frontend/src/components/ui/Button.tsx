import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Link, type LinkProps } from 'react-router-dom'
import { cn } from '@/lib/cn'
import { Spinner } from './Spinner'
import { buttonVariantClasses, type ButtonVariant } from './buttonVariants'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  carregando?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', carregando, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        data-button
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium',
          'transition-colors disabled:cursor-not-allowed disabled:opacity-60',
          buttonVariantClasses[variant],
          className,
        )}
        disabled={disabled || carregando}
        aria-busy={carregando || undefined}
        {...props}
      >
        {carregando && <Spinner size="sm" />}
        {children}
      </button>
    )
  },
)
Button.displayName = 'Button'

interface ButtonLinkProps extends LinkProps {
  variant?: ButtonVariant
}

/** Mesma aparência do Button, mas navega via react-router <Link> -
 * usar sempre que a ação é "ir para outra página", nunca um <button>
 * envolvendo um <Link> (elemento interativo dentro de interativo). */
export function ButtonLink({ className, variant = 'primary', ...props }: ButtonLinkProps) {
  return (
    <Link
      data-button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium',
        'transition-colors',
        buttonVariantClasses[variant],
        className,
      )}
      {...props}
    />
  )
}
