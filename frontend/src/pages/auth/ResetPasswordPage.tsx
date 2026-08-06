import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { InputField } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import * as authApi from '@/lib/api/auth'
import { mensagemDeErro } from '@/lib/api/errors'
import { senhaSchema } from '@/lib/validation'

const schema = z.object({ nova_senha: senhaSchema })
type FormValues = z.infer<typeof schema>

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const navigate = useNavigate()
  const [erroGeral, setErroGeral] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await authApi.redefinirSenha(token, values.nova_senha)
      setSucesso(true)
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  if (!token) {
    return (
      <AuthLayout title="Link inválido">
        <Alert tone="danger">
          Este link de redefinição de senha está incompleto. Solicite um novo link.
        </Alert>
        <Link to="/esqueci-senha" className="mt-4 block text-center text-sm text-[var(--color-primary)] hover:underline">
          Solicitar novo link
        </Link>
      </AuthLayout>
    )
  }

  if (sucesso) {
    return (
      <AuthLayout title="Senha redefinida!">
        <Alert tone="success">Sua senha foi alterada com sucesso.</Alert>
        <Button className="mt-4 w-full justify-center" onClick={() => navigate('/login')}>
          Ir para o login
        </Button>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Redefinir senha" subtitle="Escolha uma nova senha para sua conta.">
      <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
        <InputField
          label="Nova senha"
          type="password"
          autoComplete="new-password"
          ajuda="Mínimo 8 caracteres, com pelo menos uma letra e um número."
          erro={errors.nova_senha?.message}
          {...register('nova_senha')}
        />
        <Button type="submit" carregando={isSubmitting} className="mt-2 justify-center">
          Redefinir senha
        </Button>
      </form>
    </AuthLayout>
  )
}
