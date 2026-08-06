import {
  forwardRef,
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type TextareaHTMLAttributes,
} from 'react'
import { cn } from '@/lib/cn'

interface FieldWrapperProps {
  label: string
  erro?: string
  ajuda?: string
  children: (id: string, describedBy: string | undefined) => ReactNode
  className?: string
}

/** Envolve qualquer controle de formulário com <label> associado (`for`/
 * `id`), texto de ajuda e mensagem de erro ligados via `aria-describedby`
 * - nenhum campo do app deve ser renderizado sem isso (WCAG 1.3.1/3.3.2). */
export function FieldWrapper({ label, erro, ajuda, children, className }: FieldWrapperProps) {
  const id = useId()
  const ajudaId = ajuda ? `${id}-ajuda` : undefined
  const erroId = erro ? `${id}-erro` : undefined
  const describedBy = [ajudaId, erroId].filter(Boolean).join(' ') || undefined

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label htmlFor={id} className="text-sm font-medium text-[var(--color-fg)]">
        {label}
      </label>
      {children(id, describedBy)}
      {ajuda && (
        <p id={ajudaId} className="text-xs text-[var(--color-muted)]">
          {ajuda}
        </p>
      )}
      {erro && (
        <p id={erroId} role="alert" className="text-xs font-medium text-[var(--color-danger)]">
          {erro}
        </p>
      )}
    </div>
  )
}

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  erro?: string
  ajuda?: string
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  ({ label, erro, ajuda, className, ...props }, ref) => (
    <FieldWrapper label={label} erro={erro} ajuda={ajuda}>
      {(id, describedBy) => (
        <input
          ref={ref}
          id={id}
          aria-describedby={describedBy}
          aria-invalid={!!erro || undefined}
          className={cn(
            'rounded-md border bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-fg)]',
            'placeholder:text-[var(--color-muted)]',
            erro ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]',
            className,
          )}
          {...props}
        />
      )}
    </FieldWrapper>
  ),
)
InputField.displayName = 'InputField'

interface TextareaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
  erro?: string
  ajuda?: string
}

export const TextareaField = forwardRef<HTMLTextAreaElement, TextareaFieldProps>(
  ({ label, erro, ajuda, className, ...props }, ref) => (
    <FieldWrapper label={label} erro={erro} ajuda={ajuda}>
      {(id, describedBy) => (
        <textarea
          ref={ref}
          id={id}
          aria-describedby={describedBy}
          aria-invalid={!!erro || undefined}
          className={cn(
            'rounded-md border bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-fg)]',
            'placeholder:text-[var(--color-muted)]',
            erro ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]',
            className,
          )}
          {...props}
        />
      )}
    </FieldWrapper>
  ),
)
TextareaField.displayName = 'TextareaField'
