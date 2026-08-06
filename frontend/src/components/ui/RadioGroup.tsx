import * as RadioGroupPrimitive from '@radix-ui/react-radio-group'
import { useId } from 'react'
import { cn } from '@/lib/cn'

interface Opcao {
  value: string
  label: string
  descricao?: string
}

interface RadioGroupFieldProps {
  label: string
  opcoes: Opcao[]
  value: string
  onChange: (value: string) => void
  orientacao?: 'vertical' | 'horizontal'
}

export function RadioGroupField({
  label,
  opcoes,
  value,
  onChange,
  orientacao = 'vertical',
}: RadioGroupFieldProps) {
  const groupId = useId()
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm font-medium text-[var(--color-fg)]">{label}</legend>
      <RadioGroupPrimitive.Root
        value={value}
        onValueChange={onChange}
        className={cn('flex gap-3', orientacao === 'vertical' ? 'flex-col' : 'flex-row flex-wrap')}
      >
        {opcoes.map((opcao) => {
          const id = `${groupId}-${opcao.value}`
          return (
            <div key={opcao.value} className="flex items-start gap-2.5">
              <RadioGroupPrimitive.Item
                id={id}
                value={opcao.value}
                className={cn(
                  'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border',
                  'border-[var(--color-border)] bg-[var(--color-bg)] data-[state=checked]:border-[var(--color-primary)]',
                )}
              >
                <RadioGroupPrimitive.Indicator className="h-2.5 w-2.5 rounded-full bg-[var(--color-primary)]" />
              </RadioGroupPrimitive.Item>
              <label htmlFor={id} className="cursor-pointer text-sm text-[var(--color-fg)]">
                {opcao.label}
                {opcao.descricao && (
                  <span className="block text-xs text-[var(--color-muted)]">{opcao.descricao}</span>
                )}
              </label>
            </div>
          )
        })}
      </RadioGroupPrimitive.Root>
    </fieldset>
  )
}
