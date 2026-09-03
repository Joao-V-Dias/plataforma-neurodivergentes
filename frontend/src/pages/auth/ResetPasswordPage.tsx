import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'
import { AuthLayout } from './AuthLayout'
import { Button } from '@/components/ui/Button'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { redefinirSenha } from '@/lib/api/auth'
import { paraErroApi } from '@/lib/api/errors'
import { senhaSchema } from '@/lib/validation'

const schema = z.object({ senha: senhaSchema })
type FormValues = z.infer<typeof schema>

export function ResetPasswordPage() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const navigate = useNavigate()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await redefinirSenha(token, values.senha)
      navigate('/login', { replace: true, state: { redefinida: true } })
    } catch (erro) {
      setErroGeral(paraErroApi(erro).message)
    }
  }

  if (!token) {
    return (
      <AuthLayout titulo="Link inválido" rodape={<Link to="/esqueci-senha">Solicitar novo link</Link>}>
        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>
          Este link de redefinição de senha está incompleto ou expirou.
        </p>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout titulo="Redefinir senha">
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field
          label="Nova senha"
          htmlFor="senha"
          erro={errors.senha?.message}
          obrigatorio
          dica="Mínimo 8 caracteres, com letra maiúscula, minúscula e número."
        >
          <Input
            id="senha"
            type="password"
            autoComplete="new-password"
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
          Redefinir senha
        </Button>
      </form>
    </AuthLayout>
  )
}
