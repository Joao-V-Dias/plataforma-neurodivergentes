import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { UserPlus } from 'lucide-react'
import * as usuariosApi from '@/lib/api/usuarios'
import { PAPEL_LABEL, papeisCriaveisPor, type Papel } from '@/lib/api/types'
import { useAuth } from '@/lib/auth/useAuth'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { InputField } from '@/components/ui/Input'
import { SelectField } from '@/components/ui/Select'
import { Alert } from '@/components/ui/Alert'
import { PageSpinner } from '@/components/ui/Spinner'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'
import { emailSchema, senhaSchema } from '@/lib/validation'

export function UsuariosListPage() {
  const { usuario } = useAuth()
  const [dialogAberto, setDialogAberto] = useState(false)
  const queryClient = useQueryClient()
  const { notificar } = useToast()

  const { data: usuarios, isLoading } = useQuery({
    queryKey: ['usuarios'],
    queryFn: usuariosApi.listarUsuarios,
  })

  const aprovarMutation = useMutation({
    mutationFn: usuariosApi.aprovarUsuario,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      notificar({ titulo: 'Usuário aprovado', tone: 'success' })
    },
    onError: (erro) => notificar({ titulo: 'Erro ao aprovar', descricao: mensagemDeErro(erro), tone: 'danger' }),
  })

  if (!usuario) return null
  const papeisPermitidos = papeisCriaveisPor(usuario.papel)

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader
          title="Usuários da instituição"
          description="Gerencie contas e aprove alunos auto-cadastrados."
          action={
            papeisPermitidos.length > 0 && (
              <Button onClick={() => setDialogAberto(true)}>
                <UserPlus className="h-4 w-4" aria-hidden="true" />
                Novo usuário
              </Button>
            )
          }
        />

        {isLoading && <PageSpinner label="Carregando usuários..." />}

        {usuarios && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-muted)]">
                  <th scope="col" className="py-2 pr-4 font-medium">
                    Nome
                  </th>
                  <th scope="col" className="py-2 pr-4 font-medium">
                    E-mail
                  </th>
                  <th scope="col" className="py-2 pr-4 font-medium">
                    Papel
                  </th>
                  <th scope="col" className="py-2 pr-4 font-medium">
                    Status
                  </th>
                  <th scope="col" className="py-2 pr-4 font-medium">
                    <span className="sr-only">Ações</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id} className="border-b border-[var(--color-border)] last:border-0">
                    <td className="py-2.5 pr-4">{u.nome}</td>
                    <td className="py-2.5 pr-4 text-[var(--color-muted)]">{u.email}</td>
                    <td className="py-2.5 pr-4">
                      <Badge tone="primary">{PAPEL_LABEL[u.papel]}</Badge>
                    </td>
                    <td className="py-2.5 pr-4">
                      {u.is_active ? (
                        <Badge tone="success">Ativo</Badge>
                      ) : (
                        <Badge tone="warning">Aguardando aprovação</Badge>
                      )}
                    </td>
                    <td className="py-2.5 pr-4 text-right">
                      {!u.is_active && (
                        <Button
                          variant="secondary"
                          className="px-3 py-1 text-xs"
                          carregando={aprovarMutation.isPending && aprovarMutation.variables === u.id}
                          onClick={() => aprovarMutation.mutate(u.id)}
                        >
                          Aprovar
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {usuarios.length === 0 && (
              <p className="py-6 text-center text-sm text-[var(--color-muted)]">
                Nenhum usuário cadastrado ainda.
              </p>
            )}
          </div>
        )}
      </Card>

      {papeisPermitidos.length > 0 && (
        <NovoUsuarioDialog
          open={dialogAberto}
          onOpenChange={setDialogAberto}
          papeisPermitidos={papeisPermitidos}
        />
      )}
    </div>
  )
}

const schema = z.object({
  nome: z.string().min(2, 'Informe o nome completo.'),
  email: emailSchema,
  senha: senhaSchema,
  papel: z.string().min(1, 'Selecione um papel.'),
})
type FormValues = z.infer<typeof schema>

function NovoUsuarioDialog({
  open,
  onOpenChange,
  papeisPermitidos,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  papeisPermitidos: Papel[]
}) {
  const queryClient = useQueryClient()
  const { notificar } = useToast()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { papel: papeisPermitidos[0] },
  })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await usuariosApi.criarUsuario({ ...values, papel: values.papel as Papel })
      await queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      notificar({ titulo: 'Usuário criado com sucesso', tone: 'success' })
      reset()
      onOpenChange(false)
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Novo usuário" description="A conta já nasce ativa.">
      <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
        <InputField label="Nome completo" erro={errors.nome?.message} {...register('nome')} />
        <InputField label="E-mail" type="email" erro={errors.email?.message} {...register('email')} />
        <InputField
          label="Senha temporária"
          type="password"
          ajuda="Mínimo 8 caracteres, com pelo menos uma letra e um número."
          erro={errors.senha?.message}
          {...register('senha')}
        />
        <SelectField
          label="Papel"
          value={watch('papel')}
          onChange={(v) => setValue('papel', v, { shouldValidate: true })}
          opcoes={papeisPermitidos.map((p) => ({ value: p, label: PAPEL_LABEL[p] }))}
          erro={errors.papel?.message}
        />
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" carregando={isSubmitting}>
            Criar usuário
          </Button>
        </div>
      </form>
    </Dialog>
  )
}
