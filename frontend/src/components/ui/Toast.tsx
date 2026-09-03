import * as RadixToast from '@radix-ui/react-toast'
import { AlertTriangle, CheckCircle2, Info, X } from 'lucide-react'
import { useToastStore, type ToastItem } from './useToast'
import './Toast.css'

const ICONES: Record<ToastItem['tipo'], typeof Info> = {
  info: Info,
  sucesso: CheckCircle2,
  erro: AlertTriangle,
}

export function ToastViewport() {
  const { toasts, remover } = useToastStore()
  return (
    <RadixToast.Provider swipeDirection="right" duration={5000}>
      {toasts.map((toast) => {
        const Icone = ICONES[toast.tipo]
        return (
          <RadixToast.Root
            key={toast.id}
            className={`toast toast--${toast.tipo}`}
            onOpenChange={(open) => !open && remover(toast.id)}
          >
            <Icone size={18} className="toast__icone" aria-hidden="true" />
            <div className="toast__conteudo">
              <RadixToast.Title className="toast__titulo">{toast.titulo}</RadixToast.Title>
              {toast.descricao && (
                <RadixToast.Description className="toast__descricao">
                  {toast.descricao}
                </RadixToast.Description>
              )}
            </div>
            <RadixToast.Close className="toast__fechar" aria-label="Dispensar">
              <X size={14} />
            </RadixToast.Close>
          </RadixToast.Root>
        )
      })}
      <RadixToast.Viewport className="toast__viewport" />
    </RadixToast.Provider>
  )
}
