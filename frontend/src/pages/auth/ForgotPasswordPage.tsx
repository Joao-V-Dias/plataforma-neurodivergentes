import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { InputField } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import * as authApi from '@/lib/api/auth'
import { mensagemDeErro } from '@/lib/api/errors'
import { emailSchema } from '@/lib/validation'

const schema = z.object({ email: emailSchema })
type FormValues = z.infer<typeof schema>

export function ForgotPasswordPage() {
  const [erroGeral, setErroGeral] = useState<string | null>(null)
  const [resultado, setResultado] = useState<{ mensagem: string; token: string | null } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      const resp = await authApi.esqueciSenha(values.email)
      setResultado({ mensagem: resp.message, token: resp.reset_token })
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  return (
    <AuthLayout title="Esqueci minha senha" subtitle="Informe seu e-mail para receber o link de redefinição.">
      {resultado ? (
        <div className="flex flex-col gap-4">
          <Alert tone="success">{resultado.mensagem}</Alert>
          {resultado.token && (
            <Alert tone="info">
              Ambiente sem envio de e-mail configurado - use o link abaixo para redefinir agora:
              <br />
              <Link
                to={`/redefinir-senha?token=${encodeURIComponent(resultado.token)}`}
                className="font-medium underline"
              >
                Redefinir minha senha
              </Link>
            </Alert>
          )}
          <Link to="/login" className="text-center text-sm text-[var(--color-primary)] hover:underline">
            Voltar para o login
          </Link>
        </div>
      ) : (
        <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
          {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
          <InputField label="E-mail" type="email" autoComplete="email" erro={errors.email?.message} {...register('email')} />
          <Button type="submit" carregando={isSubmitting} className="mt-2 justify-center">
            Enviar link de redefinição
          </Button>
          <Link to="/login" className="text-center text-sm text-[var(--color-primary)] hover:underline">
            Voltar para o login
          </Link>
        </form>
      )}
    </AuthLayout>
  )
}
