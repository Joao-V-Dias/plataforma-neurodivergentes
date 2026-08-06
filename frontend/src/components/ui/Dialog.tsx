import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
}

export function Dialog({ open, onOpenChange, title, description, children, footer }: DialogProps) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-40 bg-black/50 data-[state=open]:animate-in data-[state=open]:fade-in" />
        <DialogPrimitive.Content
          data-card
          className={cn(
            'fixed left-1/2 top-1/2 z-50 w-[min(90vw,32rem)] -translate-x-1/2 -translate-y-1/2',
            'rounded-2xl bg-[var(--color-bg)] p-6 shadow-xl',
          )}
        >
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <DialogPrimitive.Title className="text-base font-semibold text-[var(--color-fg)]">
                {title}
              </DialogPrimitive.Title>
              {description && (
                <DialogPrimitive.Description className="mt-1 text-sm text-[var(--color-muted)]">
                  {description}
                </DialogPrimitive.Description>
              )}
            </div>
            <DialogPrimitive.Close
              aria-label="Fechar"
              className="rounded p-1 text-[var(--color-muted)] hover:bg-[var(--color-surface)]"
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </DialogPrimitive.Close>
          </div>
          {children}
          {footer && <div className="mt-6 flex justify-end gap-3">{footer}</div>}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}
