import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { AuthLayout } from './AuthLayout'
import { Button } from '@/components/ui/Button'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { paraErroApi } from '@/lib/api/errors'
import { useAuth } from '@/lib/auth/useAuth'
import { emailSchema } from '@/lib/validation'

const schema = z.object({
  email: emailSchema,
  senha: z.string().min(1, 'Informe sua senha.'),
})
type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { entrar } = useAuth()
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
      const usuario = await entrar(values)
      const destino = (location.state as { de?: string } | null)?.de
      if (!usuario.is_active) {
        navigate('/aguardando-aprovacao', { replace: true })
        return
      }
      navigate(destino ?? '/', { replace: true })
    } catch (erro) {
      setErroGeral(paraErroApi(erro).message)
    }
  }

  return (
    <AuthLayout
      titulo="Entrar"
      subtitulo="Acesse sua turma e continue de onde parou."
      rodape={
        <>
          Ainda não tem conta? <Link to="/cadastro">Criar conta de aluno</Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field label="E-mail" htmlFor="email" erro={errors.email?.message} obrigatorio>
          <Input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email} {...register('email')} />
        </Field>
        <Field label="Senha" htmlFor="senha" erro={errors.senha?.message} obrigatorio>
          <Input
            id="senha"
            type="password"
            autoComplete="current-password"
            aria-invalid={!!errors.senha}
            {...register('senha')}
          />
        </Field>
        {erroGeral && (
          <p className="field__erro" role="alert">
            {erroGeral}
          </p>
        )}
        <Button type="submit" carregando={isSubmitting} style={{ width: '100%', marginTop: 'var(--space-2)' }}>
          Entrar
        </Button>
      </form>
      <p style={{ textAlign: 'center', fontSize: 'var(--text-body-sm)' }}>
        <Link to="/esqueci-senha">Esqueci minha senha</Link>
      </p>
    </AuthLayout>
  )
}
