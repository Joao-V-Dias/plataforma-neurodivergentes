import * as RadixDialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import type { ReactNode } from 'react'
import './Dialog.css'

export function Dialog({
  open,
  onOpenChange,
  titulo,
  descricao,
  trigger,
  children,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  titulo: string
  descricao?: string
  trigger?: ReactNode
  children: ReactNode
}) {
  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      {trigger && <RadixDialog.Trigger asChild>{trigger}</RadixDialog.Trigger>}
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="dialog__overlay" />
        <RadixDialog.Content className="dialog__content" aria-describedby={descricao ? 'dialog-desc' : undefined}>
          <div className="dialog__header">
            <RadixDialog.Title className="dialog__titulo">{titulo}</RadixDialog.Title>
            <RadixDialog.Close className="dialog__fechar" aria-label="Fechar">
              <X size={16} />
            </RadixDialog.Close>
          </div>
          {descricao && (
            <RadixDialog.Description id="dialog-desc" className="dialog__descricao">
              {descricao}
            </RadixDialog.Description>
          )}
          <div className="dialog__corpo">{children}</div>
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  )
}
