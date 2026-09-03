import * as RadixTabs from '@radix-ui/react-tabs'
import type { ReactNode } from 'react'
import './Tabs.css'

export interface AbaDef {
  value: string
  label: string
  conteudo: ReactNode
}

export function Tabs({
  value,
  onValueChange,
  abas,
}: {
  value: string
  onValueChange: (v: string) => void
  abas: AbaDef[]
}) {
  return (
    <RadixTabs.Root value={value} onValueChange={onValueChange} className="tabs">
      <RadixTabs.List className="tabs__list">
        {abas.map((aba) => (
          <RadixTabs.Trigger key={aba.value} value={aba.value} className="tabs__trigger">
            {aba.label}
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      {abas.map((aba) => (
        <RadixTabs.Content key={aba.value} value={aba.value} className="tabs__conteudo">
          {aba.conteudo}
        </RadixTabs.Content>
      ))}
    </RadixTabs.Root>
  )
}
