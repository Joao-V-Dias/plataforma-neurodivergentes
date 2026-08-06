import * as ToastPrimitive from '@radix-ui/react-toast'
import { createContext, useCallback, useMemo, useState, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

type ToastTone = 'success' | 'danger' | 'info'

interface ToastItem {
  id: number
  titulo: string
  descricao?: string
  tone: ToastTone
}

interface ToastContextValue {
  notificar: (toast: Omit<ToastItem, 'id'>) => void
}

// eslint-disable-next-line react-refresh/only-export-components
export const ToastContext = createContext<ToastContextValue | null>(null)

const toneClasses: Record<ToastTone, string> = {
  success: 'border-[var(--color-success)] bg-[var(--color-success-bg)] text-[var(--color-success)]',
  danger: 'border-[var(--color-danger)] bg-[var(--color-danger-bg)] text-[var(--color-danger)]',
  info: 'border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-fg)]',
}

let proximoId = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const notificar = useCallback((toast: Omit<ToastItem, 'id'>) => {
    const id = proximoId++
    setToasts((atual) => [...atual, { ...toast, id }])
  }, [])

  const remover = useCallback((id: number) => {
    setToasts((atual) => atual.filter((t) => t.id !== id))
  }, [])

  const value = useMemo(() => ({ notificar }), [notificar])

  return (
    <ToastContext.Provider value={value}>
      <ToastPrimitive.Provider swipeDirection="right" duration={6000}>
        {children}
        {toasts.map((toast) => (
          <ToastPrimitive.Root
            key={toast.id}
            onOpenChange={(open) => {
              if (!open) remover(toast.id)
            }}
            className={cn(
              'rounded-lg border p-4 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out',
              toneClasses[toast.tone],
            )}
          >
            <ToastPrimitive.Title className="text-sm font-semibold">{toast.titulo}</ToastPrimitive.Title>
            {toast.descricao && (
              <ToastPrimitive.Description className="mt-1 text-sm opacity-90">
                {toast.descricao}
              </ToastPrimitive.Description>
            )}
          </ToastPrimitive.Root>
        ))}
        <ToastPrimitive.Viewport className="fixed bottom-0 right-0 z-[100] flex w-96 max-w-[100vw] flex-col gap-2 p-4" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  )
}
