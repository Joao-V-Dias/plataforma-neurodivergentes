import { useQueryClient } from '@tanstack/react-query'
import { useRef, useState, type ChangeEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { RadioGroup } from '@/components/ui/RadioGroup'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import { useAuth } from '@/lib/auth/useAuth'
import { enviarFotoPerfilServidor, removerFotoPerfilServidor } from './api'
import { arquivoParaDataUrl, removerFotoLocal, salvarFotoLocal } from './armazenamentoLocal'
import { useMinhaFotoUrl } from './useFotoPerfil'
import './FotoPerfilCampo.css'

const TIPOS_ACEITOS = ['image/jpeg', 'image/png', 'image/webp']
const TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024

export function FotoPerfilCampo() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const fotoAtualUrl = useMinhaFotoUrl()
  const inputRef = useRef<HTMLInputElement>(null)

  const [preview, setPreview] = useState<string | null>(null)
  const [arquivoSelecionado, setArquivoSelecionado] = useState<File | null>(null)
  const [destino, setDestino] = useState<'servidor' | 'local'>('servidor')
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  if (!usuario) return null
  const usuarioId = usuario.id

  function escolherArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const arquivo = evento.target.files?.[0]
    evento.target.value = ''
    if (!arquivo) return

    if (!TIPOS_ACEITOS.includes(arquivo.type)) {
      setErro('Use uma imagem JPEG, PNG ou WebP.')
      return
    }
    if (arquivo.size > TAMANHO_MAXIMO_BYTES) {
      setErro('A imagem precisa ter no máximo 5 MB.')
      return
    }

    setErro(null)
    setArquivoSelecionado(arquivo)
    setPreview(URL.createObjectURL(arquivo))
  }

  function limparSelecao() {
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setArquivoSelecionado(null)
  }

  async function salvar() {
    if (!arquivoSelecionado) return
    setSalvando(true)
    try {
      if (destino === 'servidor') {
        await enviarFotoPerfilServidor(arquivoSelecionado)
        await queryClient.invalidateQueries({ queryKey: ['minha-foto'] })
      } else {
        const dataUrl = await arquivoParaDataUrl(arquivoSelecionado)
        salvarFotoLocal(usuarioId, dataUrl)
      }
      limparSelecao()
      toast({ tipo: 'sucesso', titulo: 'Foto de perfil atualizada' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível salvar a foto', descricao: paraErroApi(e).message })
    } finally {
      setSalvando(false)
    }
  }

  async function remover() {
    setSalvando(true)
    try {
      await removerFotoPerfilServidor()
      await queryClient.invalidateQueries({ queryKey: ['minha-foto'] })
      removerFotoLocal(usuarioId)
      toast({ tipo: 'sucesso', titulo: 'Foto removida' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível remover a foto', descricao: paraErroApi(e).message })
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="foto-perfil-campo">
      <div className="foto-perfil-campo__pre-visualizacao">
        {preview ? (
          <img src={preview} alt="Pré-visualização da nova foto" />
        ) : fotoAtualUrl ? (
          <img src={fotoAtualUrl} alt="Sua foto de perfil atual" />
        ) : (
          <span className="foto-perfil-campo__sem-foto">Sem foto</span>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={TIPOS_ACEITOS.join(',')}
        onChange={escolherArquivo}
        hidden
        aria-label="Escolher foto de perfil"
      />

      {erro && (
        <p className="field__erro" role="alert">
          {erro}
        </p>
      )}

      {arquivoSelecionado ? (
        <div className="foto-perfil-campo__confirmacao">
          <RadioGroup
            name="foto-destino"
            value={destino}
            onValueChange={(v) => setDestino(v as 'servidor' | 'local')}
            opcoes={[
              {
                value: 'servidor',
                label: 'Salvar no servidor',
                descricao: 'Fica visível para colegas e professores da turma, em qualquer dispositivo.',
              },
              {
                value: 'local',
                label: 'Salvar só neste navegador',
                descricao: 'Mais privado: a foto não sai deste dispositivo nem é enviada ao servidor.',
              },
            ]}
          />
          <div className="foto-perfil-campo__acoes">
            <Button type="button" carregando={salvando} onClick={() => void salvar()}>
              Salvar
            </Button>
            <Button type="button" variante="fantasma" disabled={salvando} onClick={limparSelecao}>
              Cancelar
            </Button>
          </div>
        </div>
      ) : (
        <div className="foto-perfil-campo__acoes">
          <Button type="button" variante="secundario" onClick={() => inputRef.current?.click()}>
            Escolher foto
          </Button>
          {fotoAtualUrl && (
            <Button type="button" variante="fantasma" carregando={salvando} onClick={() => void remover()}>
              Remover foto
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
