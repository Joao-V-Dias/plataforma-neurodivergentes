import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { ErrorState } from '@/components/ui/EmptyState'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { PageSpinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { toast } from '@/components/ui/useToast'
import { paraErroApi } from '@/lib/api/errors'
import { criarUsuario, listarUsuarios } from '@/lib/api/usuarios'
import { PAPEL_LABEL, papeisCriaveisPor, type Papel } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'
import './DashboardTurmasPage.css'

export function UsuariosPage() {
  const { usuario } = useAuth()
  const queryClient = useQueryClient()
  const usuariosQuery = useQuery({ queryKey: ['usuarios'], queryFn: () => listarUsuarios() })
  const papeisPermitidos = usuario ? papeisCriaveisPor(usuario.papel) : []

  const [dialogoAberto, setDialogoAberto] = useState(false)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [papel, setPapel] = useState<Papel | ''>('')
  const [criando, setCriando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  async function criar() {
    if (!nome.trim() || !email.trim() || !senha.trim() || !papel) return
    setErro(null)
    setCriando(true)
    try {
      await criarUsuario({ nome, email, senha, papel })
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      setDialogoAberto(false)
      setNome('')
      setEmail('')
      setSenha('')
      setPapel('')
      toast({ tipo: 'sucesso', titulo: 'Usuário criado' })
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setCriando(false)
    }
  }

  return (
    <div>
      <header className="gestao-topo">
        <div>
          <h1>Usuários</h1>
          <p>Todos os usuários da sua instituição.</p>
        </div>
        {papeisPermitidos.length > 0 && (
          <Dialog open={dialogoAberto} onOpenChange={setDialogoAberto} titulo="Novo usuário" trigger={<Button>Novo usuário</Button>}>
            <div className="gestao-form">
              <Field label="Nome" htmlFor="u-nome" obrigatorio>
                <Input id="u-nome" value={nome} onChange={(e) => setNome(e.target.value)} />
              </Field>
              <Field label="E-mail" htmlFor="u-email" obrigatorio>
                <Input id="u-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </Field>
              <Field label="Senha temporária" htmlFor="u-senha" obrigatorio>
                <Input id="u-senha" type="password" value={senha} onChange={(e) => setSenha(e.target.value)} />
              </Field>
              <Field label="Papel" htmlFor="u-papel" obrigatorio>
                <Select
                  id="u-papel"
                  value={papel}
                  onValueChange={(v) => setPapel(v as Papel)}
                  opcoes={papeisPermitidos.map((p) => ({ value: p, label: PAPEL_LABEL[p] }))}
                  placeholder="Selecione um papel"
                />
              </Field>
              {erro && <p className="field__erro" role="alert">{erro}</p>}
              <Button carregando={criando} onClick={() => void criar()}>
                Criar usuário
              </Button>
            </div>
          </Dialog>
        )}
      </header>

      {usuariosQuery.isLoading && <PageSpinner />}
      {usuariosQuery.isError && (
        <ErrorState mensagem={paraErroApi(usuariosQuery.error).message} onRetry={() => usuariosQuery.refetch()} />
      )}
      {usuariosQuery.data && (
        <Table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Papel</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {usuariosQuery.data.map((u) => (
              <tr key={u.id}>
                <td>{u.nome}</td>
                <td>{u.email}</td>
                <td>{PAPEL_LABEL[u.papel]}</td>
                <td>
                  <Badge tom={u.is_active ? 'sucesso' : 'aviso'}>{u.is_active ? 'Ativo' : 'Pendente'}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  )
}
