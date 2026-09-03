import * as RadixSelect from '@radix-ui/react-select'
import { Check, ChevronDown } from 'lucide-react'
import './Select.css'

export interface OpcaoSelect {
  value: string
  label: string
}

export function Select({
  id,
  value,
  onValueChange,
  opcoes,
  placeholder = 'Selecione…',
  disabled,
}: {
  id?: string
  value: string
  onValueChange: (v: string) => void
  opcoes: OpcaoSelect[]
  placeholder?: string
  disabled?: boolean
}) {
  return (
    <RadixSelect.Root value={value} onValueChange={onValueChange} disabled={disabled}>
      <RadixSelect.Trigger id={id} className="select__trigger" aria-label={placeholder}>
        <RadixSelect.Value placeholder={placeholder} />
        <RadixSelect.Icon>
          <ChevronDown size={16} />
        </RadixSelect.Icon>
      </RadixSelect.Trigger>
      <RadixSelect.Portal>
        <RadixSelect.Content className="select__content" position="popper" sideOffset={4}>
          <RadixSelect.Viewport>
            {opcoes.map((opcao) => (
              <RadixSelect.Item key={opcao.value} value={opcao.value} className="select__item">
                <RadixSelect.ItemText>{opcao.label}</RadixSelect.ItemText>
                <RadixSelect.ItemIndicator className="select__indicator">
                  <Check size={14} />
                </RadixSelect.ItemIndicator>
              </RadixSelect.Item>
            ))}
          </RadixSelect.Viewport>
        </RadixSelect.Content>
      </RadixSelect.Portal>
    </RadixSelect.Root>
  )
}
