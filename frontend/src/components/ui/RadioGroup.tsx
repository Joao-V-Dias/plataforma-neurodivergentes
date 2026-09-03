import * as RadixRadio from '@radix-ui/react-radio-group'
import './RadioGroup.css'

export interface OpcaoRadio {
  value: string
  label: string
  descricao?: string
}

export function RadioGroup({
  name,
  value,
  onValueChange,
  opcoes,
  orientacao = 'vertical',
}: {
  name: string
  value: string
  onValueChange: (v: string) => void
  opcoes: OpcaoRadio[]
  orientacao?: 'vertical' | 'horizontal'
}) {
  return (
    <RadixRadio.Root
      name={name}
      value={value}
      onValueChange={onValueChange}
      className={`radiogroup radiogroup--${orientacao}`}
    >
      {opcoes.map((opcao) => (
        <label className="radiogroup__item" key={opcao.value} htmlFor={`${name}-${opcao.value}`}>
          <RadixRadio.Item id={`${name}-${opcao.value}`} value={opcao.value} className="radiogroup__control">
            <RadixRadio.Indicator className="radiogroup__indicator" />
          </RadixRadio.Item>
          <span>
            <span className="radiogroup__label">{opcao.label}</span>
            {opcao.descricao && <span className="radiogroup__descricao">{opcao.descricao}</span>}
          </span>
        </label>
      ))}
    </RadixRadio.Root>
  )
}
