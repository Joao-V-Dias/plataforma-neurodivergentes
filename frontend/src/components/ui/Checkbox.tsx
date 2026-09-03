import * as RadixCheckbox from '@radix-ui/react-checkbox'
import { Check } from 'lucide-react'
import './Checkbox.css'

export function Checkbox({
  id,
  checked,
  onCheckedChange,
  label,
  disabled,
}: {
  id: string
  checked: boolean
  onCheckedChange: (v: boolean) => void
  label: string
  disabled?: boolean
}) {
  return (
    <label className="checkbox" htmlFor={id}>
      <RadixCheckbox.Root
        id={id}
        className="checkbox__box"
        checked={checked}
        onCheckedChange={(v) => onCheckedChange(v === true)}
        disabled={disabled}
      >
        <RadixCheckbox.Indicator className="checkbox__indicator">
          <Check size={13} strokeWidth={3} />
        </RadixCheckbox.Indicator>
      </RadixCheckbox.Root>
      <span>{label}</span>
    </label>
  )
}
