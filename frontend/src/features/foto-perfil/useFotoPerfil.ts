import { useQuery } from '@tanstack/react-query'
import { useEffect, useReducer, useState } from 'react'
import { useAuth } from '@/lib/auth/useAuth'
import { baixarFotoDeUsuario, obterMinhaFotoServidor } from './api'
import { assinarMudancaFotoLocal, obterFotoLocal } from './armazenamentoLocal'

/** Resolve a foto de perfil do usuário logado, com prioridade pro servidor
 * (visível em qualquer dispositivo e pra outras pessoas); se não houver,
 * cai pra foto salva só neste navegador; se nenhuma existir, retorna null
 * (quem usa mostra o avatar de ícone nesse caso). */
export function useMinhaFotoUrl(): string | null {
  const { usuario } = useAuth()
  const servidorQuery = useQuery({
    queryKey: ['minha-foto'],
    queryFn: obterMinhaFotoServidor,
    enabled: !!usuario,
  })
  const [blobUrl, setBlobUrl] = useState<string | null>(null)
  const [, forcarAtualizacao] = useReducer((c: number) => c + 1, 0)

  useEffect(() => assinarMudancaFotoLocal(forcarAtualizacao), [])

  useEffect(() => {
    if (!usuario?.id || !servidorQuery.data) return
    let objectUrl: string | null = null
    let cancelado = false
    void baixarFotoDeUsuario(usuario.id).then((blob) => {
      if (cancelado) return
      objectUrl = URL.createObjectURL(blob)
      setBlobUrl(objectUrl)
    })
    return () => {
      cancelado = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [usuario?.id, servidorQuery.data])

  if (!usuario) return null
  if (servidorQuery.data) return blobUrl
  if (!servidorQuery.isLoading) return obterFotoLocal(usuario.id)
  return null
}
