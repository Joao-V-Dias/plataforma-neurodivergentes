import { useSyncExternalStore } from 'react'

export interface ToastItem {
  id: number
  tipo: 'info' | 'sucesso' | 'erro'
  titulo: string
  descricao?: string
}

let toasts: ToastItem[] = []
let idSeq = 0
const listeners = new Set<() => void>()

function emit() {
  listeners.forEach((l) => l())
}

export function toast(item: Omit<ToastItem, 'id'>) {
  idSeq += 1
  toasts = [...toasts, { ...item, id: idSeq }]
  emit()
}

function remover(id: number) {
  toasts = toasts.filter((t) => t.id !== id)
  emit()
}

export function useToastStore() {
  const lista = useSyncExternalStore(
    (cb) => {
      listeners.add(cb)
      return () => listeners.delete(cb)
    },
    () => toasts,
  )
  return { toasts: lista, remover }
}
