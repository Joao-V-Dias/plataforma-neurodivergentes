import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import * as turmasApi from '@/lib/api/turmas'
import * as usuariosApi from '@/lib/api/usuarios'
import { Dialog } from '@/components/ui/Dialog'
import { InputField } from '@/components/ui/Input'
import { SelectField } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { mensagemDeErro } from '@/lib/api/errors'

const schema = z.object({
  nome: z.string().min(2, 'Informe o nome da turma.'),
  periodo: z.string().min(1, 'Informe o período (ex: 2026.1).'),
  professor_responsavel_id: z.string().min(1, 'Selecione o professor responsável.'),
})
type FormValues = z.infer<typeof schema>

export function NovaTurmaDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const queryClient = useQueryClient()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const { data: usuarios } = useQuery({
    queryKey: ['usuarios'],
    queryFn: usuariosApi.listarUsuarios,
    enabled: open,
  })
  const professores = (usuarios ?? []).filter((u) => u.papel === 'professor' && u.is_active)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setErroGeral(null)
    try {
      await turmasApi.criarTurma(values)
      await queryClient.invalidateQueries({ queryKey: ['turmas'] })
      reset()
      onOpenChange(false)
    } catch (erro) {
      setErroGeral(mensagemDeErro(erro))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Nova turma">
      <form className="flex flex-col gap-4" onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate>
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}
        <InputField label="Nome da turma" erro={errors.nome?.message} {...register('nome')} />
        <InputField label="Período" placeholder="2026.1" erro={errors.periodo?.message} {...register('periodo')} />
        <SelectField
          label="Professor responsável"
          value={watch('professor_responsavel_id') ?? ''}
          onChange={(v) => setValue('professor_responsavel_id', v, { shouldValidate: true })}
          opcoes={professores.map((p) => ({ value: p.id, label: p.nome }))}
          placeholder={professores.length === 0 ? 'Nenhum professor disponível' : 'Selecione...'}
          erro={errors.professor_responsavel_id?.message}
          disabled={professores.length === 0}
        />
        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" carregando={isSubmitting}>
            Criar turma
          </Button>
        </div>
      </form>
    </Dialog>
  )
}
