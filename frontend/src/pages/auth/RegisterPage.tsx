import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { AuthLayout } from './AuthLayout'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { registrar } from '@/lib/api/auth'
import { paraErroApi } from '@/lib/api/errors'
import { emailSchema, senhaSchema } from '@/lib/validation'

const schema = z.object({
  nome: z.string().min(2, 'Informe seu nome completo.').max(200),
  email: emailSchema,
  senha: senhaSchema,
  instituicao_codigo: z.string().min(1, 'Informe o código da sua instituição.'),
  aceite_lgpd: z.literal(true, {
    error: 'É necessário aceitar os termos de tratamento de dados.',
  }),
})
type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const navigate = useNavigate()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const {
    register: reg,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { aceite_lgpd: undefined },
  })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await registrar(values)
      navigate('/cadastro-enviado', { replace: true })
    } catch (erro) {
      setErroGeral(paraErroApi(erro).message)
    }
  }

  return (
    <AuthLayout
      titulo="Criar conta"
      subtitulo="Cadastro de aluno. Sua conta é ativada por um professor da sua instituição."
      rodape={
        <>
          Já tem conta? <Link to="/login">Entrar</Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Field label="Nome" htmlFor="nome" erro={errors.nome?.message} obrigatorio>
          <Input id="nome" autoComplete="name" aria-invalid={!!errors.nome} {...reg('nome')} />
        </Field>
        <Field label="E-mail" htmlFor="email" erro={errors.email?.message} obrigatorio>
          <Input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email} {...reg('email')} />
        </Field>
        <Field label="Senha" htmlFor="senha" erro={errors.senha?.message} obrigatorio dica="Mínimo 8 caracteres, com letra maiúscula, minúscula e número.">
          <Input
            id="senha"
            type="password"
            autoComplete="new-password"
            aria-invalid={!!errors.senha}
            {...reg('senha')}
          />
        </Field>
        <Field
          label="Código da instituição"
          htmlFor="instituicao_codigo"
          erro={errors.instituicao_codigo?.message}
          dica="Fornecido pela sua escola ou professor."
          obrigatorio
        >
          <Input id="instituicao_codigo" aria-invalid={!!errors.instituicao_codigo} {...reg('instituicao_codigo')} />
        </Field>
        <Controller
          control={control}
          name="aceite_lgpd"
          render={({ field }) => (
            <Checkbox
              id="aceite_lgpd"
              checked={field.value === true}
              onCheckedChange={(v) => field.onChange(v)}
              label="Li e aceito o tratamento dos meus dados de cadastro conforme a política de privacidade."
            />
          )}
        />
        {errors.aceite_lgpd && (
          <p className="field__erro" role="alert">
            {errors.aceite_lgpd.message}
          </p>
        )}
        {erroGeral && (
          <p className="field__erro" role="alert">
            {erroGeral}
          </p>
        )}
        <Button type="submit" carregando={isSubmitting} style={{ width: '100%', marginTop: 'var(--space-2)' }}>
          Criar conta
        </Button>
      </form>
    </AuthLayout>
  )
}
