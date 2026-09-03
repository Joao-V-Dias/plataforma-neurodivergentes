import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { AuthLayout } from './AuthLayout'
import { Button } from '@/components/ui/Button'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { esqueciSenha } from '@/lib/api/auth'
import { paraErroApi } from '@/lib/api/errors'
import { emailSchema } from '@/lib/validation'

const schema = z.object({ email: emailSchema })
type FormValues = z.infer<typeof schema>

export function ForgotPasswordPage() {
  const [mensagem, setMensagem] = useState<string | null>(null)
  const [erroGeral, setErroGeral] = useState<string | null>(null)
  const [tokenDev, setTokenDev] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    setMensagem(null)
    try {
      const resp = await esqueciSenha(values.email)
      setMensagem(resp.message)
      setTokenDev(resp.reset_token)
    } catch (erro) {
      setErroGeral(paraErroApi(erro).message)
    }
  }

  return (
    <AuthLayout
      titulo="Esqueci minha senha"
      subtitulo="Enviaremos um link de redefinição para o seu e-mail, se ele estiver cadastrado."
      rodape={<Link to="/login">Voltar para o login</Link>}
    >
      {mensagem ? (
        <div>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>{mensagem}</p>
          {tokenDev && (
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--text-muted)', marginTop: 'var(--space-3)' }}>
              Ambiente de desenvolvimento — token: <Link to={`/redefinir-senha?token=${tokenDev}`}>{tokenDev}</Link>
            </p>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Field label="E-mail" htmlFor="email" erro={errors.email?.message} obrigatorio>
            <Input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email} {...register('email')} />
          </Field>
          {erroGeral && (
            <p className="field__erro" role="alert">
              {erroGeral}
            </p>
          )}
          <Button type="submit" carregando={isSubmitting} style={{ width: '100%', marginTop: 'var(--space-2)' }}>
            Enviar link
          </Button>
        </form>
      )}
    </AuthLayout>
  )
}
