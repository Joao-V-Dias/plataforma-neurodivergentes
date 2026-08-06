import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { InputField } from '@/components/ui/Input'
import { CheckboxField } from '@/components/ui/Checkbox'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import * as authApi from '@/lib/api/auth'
import { mensagemDeErro } from '@/lib/api/errors'
import { emailSchema, senhaSchema } from '@/lib/validation'

const schema = z.object({
  nome: z.string().min(2, 'Informe seu nome completo.'),
  email: emailSchema,
  senha: senhaSchema,
  instituicao_codigo: z.string().min(1, 'Informe o código da sua instituição.'),
  aceite_lgpd: z
    .boolean()
    .refine((v) => v === true, 'É necessário aceitar o tratamento de dados para se cadastrar.'),
})
type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const navigate = useNavigate()
  const [erroGeral, setErroGeral] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { aceite_lgpd: false },
  })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await authApi.registrar(values)
      setSucesso(true)
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  if (sucesso) {
    return (
      <AuthLayout title="Cadastro recebido!">
        <Alert tone="success">
          Sua conta foi criada e está aguardando aprovação de um professor ou coordenador da sua
          instituição. Você receberá acesso assim que ela for aprovada.
        </Alert>
        <Button className="mt-4 w-full justify-center" onClick={() => navigate('/login')}>
          Voltar para o login
        </Button>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Criar conta de aluno" subtitle="Sua conta ficará pendente até ser aprovada pela escola.">
      <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
        <InputField label="Nome completo" erro={errors.nome?.message} {...register('nome')} />
        <InputField label="E-mail" type="email" autoComplete="email" erro={errors.email?.message} {...register('email')} />
        <InputField
          label="Senha"
          type="password"
          autoComplete="new-password"
          ajuda="Mínimo 8 caracteres, com pelo menos uma letra e um número."
          erro={errors.senha?.message}
          {...register('senha')}
        />
        <InputField
          label="Código da instituição"
          ajuda="Fornecido pela sua escola/curso."
          erro={errors.instituicao_codigo?.message}
          {...register('instituicao_codigo')}
        />
        <CheckboxField
          label="Estou de acordo com o tratamento dos meus dados pessoais para fins educacionais (LGPD)."
          checked={watch('aceite_lgpd')}
          onChange={(checked) => setValue('aceite_lgpd', checked, { shouldValidate: true })}
        />
        {errors.aceite_lgpd && (
          <p role="alert" className="text-xs font-medium text-[var(--color-danger)]">
            {errors.aceite_lgpd.message}
          </p>
        )}
        <Button type="submit" carregando={isSubmitting} className="mt-2 justify-center">
          Criar conta
        </Button>
        <p className="text-center text-sm text-[var(--color-muted)]">
          Já tem conta?{' '}
          <Link to="/login" className="text-[var(--color-primary)] hover:underline">
            Entrar
          </Link>
        </p>
      </form>
    </AuthLayout>
  )
}
