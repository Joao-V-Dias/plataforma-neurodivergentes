import * as CheckboxPrimitive from '@radix-ui/react-checkbox'
import * as SwitchPrimitive from '@radix-ui/react-switch'
import { Check } from 'lucide-react'
import { useId, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface CheckboxFieldProps {
  label: ReactNode
  checked: boolean
  onChange: (checked: boolean) => void
  descricao?: string
  disabled?: boolean
}

export function CheckboxField({ label, checked, onChange, descricao, disabled }: CheckboxFieldProps) {
  const id = useId()
  return (
    <div className="flex items-start gap-2.5">
      <CheckboxPrimitive.Root
        id={id}
        checked={checked}
        onCheckedChange={(v) => onChange(v === true)}
        disabled={disabled}
        className={cn(
          'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border',
          'border-[var(--color-border)] bg-[var(--color-bg)] data-[state=checked]:bg-[var(--color-primary)]',
          'data-[state=checked]:border-[var(--color-primary)] disabled:cursor-not-allowed disabled:opacity-60',
        )}
      >
        <CheckboxPrimitive.Indicator>
          <Check className="h-3.5 w-3.5 text-[var(--color-primary-fg)]" aria-hidden="true" />
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      <div>
        <label htmlFor={id} className="cursor-pointer text-sm font-medium text-[var(--color-fg)]">
          {label}
        </label>
        {descricao && <p className="text-xs text-[var(--color-muted)]">{descricao}</p>}
      </div>
    </div>
  )
}

interface SwitchFieldProps {
  label: ReactNode
  checked: boolean
  onChange: (checked: boolean) => void
  descricao?: string
  disabled?: boolean
}

export function SwitchField({ label, checked, onChange, descricao, disabled }: SwitchFieldProps) {
  const id = useId()
  return (
    <div className="flex items-center justify-between gap-4 py-1.5">
      <div>
        <label htmlFor={id} className="cursor-pointer text-sm font-medium text-[var(--color-fg)]">
          {label}
        </label>
        {descricao && <p className="text-xs text-[var(--color-muted)]">{descricao}</p>}
      </div>
      <SwitchPrimitive.Root
        id={id}
        checked={checked}
        onCheckedChange={onChange}
        disabled={disabled}
        className={cn(
          'relative h-6 w-11 shrink-0 rounded-full border border-[var(--color-border)] transition-colors',
          'bg-[var(--color-surface)] data-[state=checked]:bg-[var(--color-primary)]',
          'disabled:cursor-not-allowed disabled:opacity-60',
        )}
      >
        <SwitchPrimitive.Thumb
          className={cn(
            'block h-[18px] w-[18px] translate-x-1 rounded-full bg-[var(--color-bg)] shadow transition-transform',
            'data-[state=checked]:translate-x-6',
          )}
        />
      </SwitchPrimitive.Root>
    </div>
  )
}
