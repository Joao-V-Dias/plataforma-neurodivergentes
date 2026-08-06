import * as SelectPrimitive from '@radix-ui/react-select'
import { Check, ChevronDown } from 'lucide-react'
import { useId } from 'react'
import { cn } from '@/lib/cn'

interface Opcao {
  value: string
  label: string
}

interface SelectFieldProps {
  label: string
  opcoes: Opcao[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  erro?: string
  ajuda?: string
  disabled?: boolean
}

export function SelectField({
  label,
  opcoes,
  value,
  onChange,
  placeholder = 'Selecione...',
  erro,
  ajuda,
  disabled,
}: SelectFieldProps) {
  const id = useId()
  const ajudaId = ajuda ? `${id}-ajuda` : undefined
  const erroId = erro ? `${id}-erro` : undefined

  return (
    <div className="flex flex-col gap-1.5">
      <label id={`${id}-label`} htmlFor={id} className="text-sm font-medium text-[var(--color-fg)]">
        {label}
      </label>
      <SelectPrimitive.Root value={value} onValueChange={onChange} disabled={disabled}>
        <SelectPrimitive.Trigger
          id={id}
          aria-labelledby={`${id}-label`}
          aria-describedby={[ajudaId, erroId].filter(Boolean).join(' ') || undefined}
          aria-invalid={!!erro || undefined}
          className={cn(
            'flex items-center justify-between gap-2 rounded-lg border bg-[var(--color-bg)] px-3 py-2 text-sm',
            'text-[var(--color-fg)] disabled:cursor-not-allowed disabled:opacity-60',
            erro ? 'border-[var(--color-danger)]' : 'border-[var(--color-border)]',
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon>
            <ChevronDown className="h-4 w-4 opacity-70" aria-hidden="true" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            className="z-50 overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-lg"
            position="popper"
            sideOffset={4}
          >
            <SelectPrimitive.Viewport className="p-1">
              {opcoes.map((opcao) => (
                <SelectPrimitive.Item
                  key={opcao.value}
                  value={opcao.value}
                  className={cn(
                    'flex cursor-pointer items-center justify-between gap-2 rounded px-2 py-1.5 text-sm',
                    'text-[var(--color-fg)] outline-none data-[highlighted]:bg-[var(--color-surface)]',
                  )}
                >
                  <SelectPrimitive.ItemText>{opcao.label}</SelectPrimitive.ItemText>
                  <SelectPrimitive.ItemIndicator>
                    <Check className="h-4 w-4" aria-hidden="true" />
                  </SelectPrimitive.ItemIndicator>
                </SelectPrimitive.Item>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>
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
