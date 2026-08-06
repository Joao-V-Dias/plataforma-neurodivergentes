import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Link, useLocation, useNavigate, type Location } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { InputField } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { useAuth } from '@/lib/auth/useAuth'
import { mensagemDeErro } from '@/lib/api/errors'
import { emailSchema } from '@/lib/validation'

const schema = z.object({
  email: emailSchema,
  senha: z.string().min(1, 'Informe sua senha.'),
})
type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await login(values.email, values.senha)
      const estado = location.state as { from?: Location } | null
      const destino = estado?.from?.pathname ?? '/'
      navigate(destino, { replace: true })
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  return (
    <AuthLayout title="Entrar" subtitle="Acesse sua conta para continuar.">
      <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
        <InputField
          label="E-mail"
          type="email"
          autoComplete="email"
          erro={errors.email?.message}
          {...register('email')}
        />
        <InputField
          label="Senha"
          type="password"
          autoComplete="current-password"
          erro={errors.senha?.message}
          {...register('senha')}
        />
        <Button type="submit" carregando={isSubmitting} className="mt-2 justify-center">
          Entrar
        </Button>
        <div className="flex justify-between text-sm">
          <Link to="/esqueci-senha" className="text-[var(--color-primary)] hover:underline">
            Esqueci minha senha
          </Link>
          <Link to="/cadastro" className="text-[var(--color-primary)] hover:underline">
            Criar conta de aluno
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
