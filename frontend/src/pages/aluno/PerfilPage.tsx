import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Avatar } from '@/components/ui/Avatar'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Dialog } from '@/components/ui/Dialog'
import { EmptyState, ErrorState } from '@/components/ui/EmptyState'
import { Field } from '@/components/ui/Field'
import { Input, Textarea } from '@/components/ui/Input'
import { PageSpinner } from '@/components/ui/Spinner'
import { Tabs } from '@/components/ui/Tabs'
import { CamposAcessibilidade } from '@/components/layout/CamposAcessibilidade'
import { FotoPerfilCampo } from '@/features/foto-perfil/FotoPerfilCampo'
import { paraErroApi } from '@/lib/api/errors'
import { obterMeuAvatar, atualizarMeuAvatar } from '@/lib/api/gamificacao'
import { listarCondicoes, obterHistoricoPerfilAluno, registrarPerfilAluno } from '@/lib/api/perfis'
import { AVATARES, AVATAR_LABEL, type AvatarCodigo } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'
import { toast } from '@/components/ui/useToast'
import './PerfilPage.css'

export function PerfilPage() {
  const [aba, setAba] = useState('avatar')
  return (
    <div className="perfil-pagina">
      <h1>Meu perfil</h1>
      <Tabs
        value={aba}
        onValueChange={setAba}
        abas={[
          { value: 'avatar', label: 'Avatar e apelido', conteudo: <AbaAvatar /> },
          { value: 'acessibilidade', label: 'Acessibilidade', conteudo: <CamposAcessibilidade /> },
          { value: 'neurodivergencia', label: 'Perfil de neurodivergência', conteudo: <AbaNeurodivergencia /> },
        ]}
      />
    </div>
  )
}

function AbaAvatar() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const avatarQuery = useQuery({ queryKey: ['meu-avatar'], queryFn: obterMeuAvatar })
  const [apelido, setApelido] = useState<string | null>(null)
  const [avatarCodigo, setAvatarCodigo] = useState<AvatarCodigo | null | undefined>(undefined)
  const [salvando, setSalvando] = useState(false)

  if (avatarQuery.isLoading) return <PageSpinner />
  if (avatarQuery.isError) {
    return <ErrorState mensagem={paraErroApi(avatarQuery.error).message} onRetry={() => avatarQuery.refetch()} />
  }

  const apelidoAtual = apelido ?? avatarQuery.data?.apelido ?? ''
  const avatarAtual = avatarCodigo !== undefined ? avatarCodigo : avatarQuery.data?.avatar_codigo ?? null

  async function salvar() {
    setSalvando(true)
    try {
      await atualizarMeuAvatar({ apelido: apelidoAtual || null, avatar_codigo: avatarAtual })
      await queryClient.invalidateQueries({ queryKey: ['meu-avatar'] })
      toast({ tipo: 'sucesso', titulo: 'Avatar atualizado' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível salvar', descricao: paraErroApi(e).message })
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="perfil-avatar">
      <Field label="Apelido" htmlFor="apelido-perfil" dica="Como você aparece para colegas de turma.">
        <Input
          id="apelido-perfil"
          value={apelidoAtual}
          maxLength={40}
          placeholder={usuario?.nome.split(' ')[0]}
          onChange={(e) => setApelido(e.target.value)}
        />
      </Field>

      <div className="perfil-avatar__foto">
        <h2 className="perfil-avatar__subtitulo">Foto de perfil (opcional)</h2>
        <p className="perfil-avatar__dica">
          Se você enviar uma foto, ela substitui o avatar de ícone abaixo em todo o app.
        </p>
        <FotoPerfilCampo />
      </div>

      <h2 className="perfil-avatar__subtitulo">Avatar de ícone</h2>
      <div className="perfil-avatar__grade">
        {AVATARES.map((codigo) => (
          <button
            type="button"
            key={codigo}
            className="perfil-avatar__opcao"
            data-selecionado={avatarAtual === codigo}
            onClick={() => setAvatarCodigo(codigo)}
          >
            <Avatar codigo={codigo} tamanho={44} />
            <span>{AVATAR_LABEL[codigo]}</span>
          </button>
        ))}
      </div>
      <Button carregando={salvando} onClick={() => void salvar()}>
        Salvar
      </Button>
    </div>
  )
}

function AbaNeurodivergencia() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const historicoQuery = useQuery({
    queryKey: ['historico-perfil', usuario?.id],
    queryFn: () => obterHistoricoPerfilAluno(usuario!.id),
    enabled: !!usuario,
  })
  const condicoesQuery = useQuery({ queryKey: ['condicoes'], queryFn: listarCondicoes })

  const [dialogoAberto, setDialogoAberto] = useState(false)
  const [condicoesSelecionadas, setCondicoesSelecionadas] = useState<string[]>([])
  const [observacoes, setObservacoes] = useState('')
  const [aceite, setAceite] = useState(false)
  const [enviando, setEnviando] = useState(false)

  async function enviarAtualizacao() {
    if (!usuario) return
    setEnviando(true)
    try {
      await registrarPerfilAluno(usuario.id, {
        condicoes_codigos: condicoesSelecionadas,
        observacoes: observacoes || null,
        aceite_consentimento: aceite,
      })
      await queryClient.invalidateQueries({ queryKey: ['historico-perfil', usuario.id] })
      setDialogoAberto(false)
      toast({ tipo: 'sucesso', titulo: 'Perfil atualizado' })
    } catch (e) {
      toast({ tipo: 'erro', titulo: 'Não foi possível salvar', descricao: paraErroApi(e).message })
    } finally {
      setEnviando(false)
    }
  }

  if (historicoQuery.isLoading) return <PageSpinner />

  const historico = historicoQuery.data ?? []

  return (
    <div className="perfil-neuro">
      <p className="perfil-neuro__intro">
        Cada atualização cria uma nova versão — nada é sobrescrito, e você pode ver como seu perfil
        mudou ao longo do tempo.
      </p>

      {historico.length === 0 && (
        <EmptyState titulo="Nenhum registro ainda" descricao="Você optou por não informar condições de neurodivergência." />
      )}

      {historico.length > 0 && (
        <ol className="perfil-neuro__linha-tempo">
          {historico.map((v) => (
            <li key={v.id}>
              <div className="perfil-neuro__versao-cabecalho">
                <span>Versão {v.versao}</span>
                <span>{new Date(v.criado_em).toLocaleDateString('pt-BR')}</span>
              </div>
              {v.condicoes.length > 0 ? (
                <ul className="perfil-neuro__condicoes">
                  {v.condicoes.map((c) => (
                    <li key={c.id}>{c.nome}</li>
                  ))}
                </ul>
              ) : (
                <p className="perfil-neuro__sem-condicoes">Nenhuma condição informada</p>
              )}
              {v.observacoes && <p className="perfil-neuro__observacoes">{v.observacoes}</p>}
            </li>
          ))}
        </ol>
      )}

      <Dialog
        open={dialogoAberto}
        onOpenChange={setDialogoAberto}
        titulo="Atualizar perfil"
        descricao="Isso cria uma nova versão do seu perfil de neurodivergência."
        trigger={<Button variante="secundario">Atualizar perfil</Button>}
      >
        <div className="perfil-neuro__form">
          {(condicoesQuery.data ?? []).map((c) => (
            <Checkbox
              key={c.id}
              id={`atual-${c.codigo}`}
              checked={condicoesSelecionadas.includes(c.codigo)}
              onCheckedChange={(v) =>
                setCondicoesSelecionadas((atual) => (v ? [...atual, c.codigo] : atual.filter((x) => x !== c.codigo)))
              }
              label={c.nome}
            />
          ))}
          <Field label="Observações" htmlFor="obs-atual">
            <Textarea id="obs-atual" value={observacoes} onChange={(e) => setObservacoes(e.target.value)} maxLength={2000} />
          </Field>
          <Checkbox
            id="aceite-atual"
            checked={aceite}
            onCheckedChange={setAceite}
            label="Aceito o tratamento desses dados para adaptar meu ensino."
          />
          <Button disabled={!aceite} carregando={enviando} onClick={() => void enviarAtualizacao()}>
            Salvar nova versão
          </Button>
        </div>
      </Dialog>
    </div>
  )
}
