import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useFieldArray, useForm } from 'react-hook-form'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2 } from 'lucide-react'
import * as problemasApi from '@/lib/api/problemas'
import { Card, CardHeader } from '@/components/ui/Card'
import { InputField, TextareaField } from '@/components/ui/Input'
import { SelectField } from '@/components/ui/Select'
import { CheckboxField } from '@/components/ui/Checkbox'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { PageSpinner } from '@/components/ui/Spinner'
import { mensagemDeErro } from '@/lib/api/errors'
import { NIVEL_DIFICULDADE_LABEL, type NivelDificuldade } from '@/lib/api/types'

const casoSchema = z.object({
  entrada: z.string(),
  saida_esperada: z.string().min(1, 'Informe a saída esperada.'),
  publico: z.boolean(),
})

const schema = z.object({
  titulo: z.string().min(2, 'Informe o título.'),
  enunciado: z.string().min(1, 'Informe o enunciado.'),
  nivel_dificuldade: z.string().min(1, 'Selecione o nível.'),
  tags_codigos: z.array(z.string()),
  casos: z.array(casoSchema).min(1, 'Adicione ao menos um caso de teste.'),
})
type FormValues = z.infer<typeof schema>

const NIVEIS = (['facil', 'medio', 'dificil'] as NivelDificuldade[]).map((v) => ({
  value: v,
  label: NIVEL_DIFICULDADE_LABEL[v],
}))

export function NovoProblemaPage() {
  const navigate = useNavigate()
  const [erroGeral, setErroGeral] = useState<string | null>(null)

  const { data: tags, isLoading: carregandoTags } = useQuery({
    queryKey: ['tags'],
    queryFn: () => problemasApi.listarTags(),
  })

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      nivel_dificuldade: 'facil',
      tags_codigos: [],
      casos: [{ entrada: '', saida_esperada: '', publico: true }],
    },
  })
  const { fields, append, remove } = useFieldArray({ control, name: 'casos' })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      problemasApi.criarProblema({ ...values, linguagem: 'python', nivel_dificuldade: values.nivel_dificuldade as NivelDificuldade }),
    onSuccess: (problema) => navigate(`/problemas/${problema.id}`),
    onError: (erro) => setErroGeral(mensagemDeErro(erro)),
  })

  if (carregandoTags) return <PageSpinner label="Carregando..." />

  const tagsSelecionadas = watch('tags_codigos')

  return (
    <Card className="max-w-3xl">
      <CardHeader
        title="Novo problema"
        description="Casos de teste públicos são mostrados ao aluno; ocultos servem só para corrigir."
      />
      <form
        className="flex flex-col gap-5"
        onSubmit={(e) => void handleSubmit((v) => mutation.mutate(v))(e)}
        noValidate
      >
        {erroGeral && <Alert tone="danger">{erroGeral}</Alert>}

        <InputField label="Título" erro={errors.titulo?.message} {...register('titulo')} />
        <TextareaField
          label="Enunciado"
          rows={5}
          erro={errors.enunciado?.message}
          {...register('enunciado')}
        />
        <SelectField
          label="Nível de dificuldade"
          value={watch('nivel_dificuldade')}
          onChange={(v) => setValue('nivel_dificuldade', v)}
          opcoes={NIVEIS}
        />

        {tags && tags.length > 0 && (
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-[var(--color-fg)]">Tags</legend>
            <div className="flex flex-col gap-2">
              {tags.map((tag) => (
                <CheckboxField
                  key={tag.id}
                  label={`${tag.nome} (${tag.categoria === 'raciocinio' ? 'raciocínio' : 'tema'})`}
                  checked={tagsSelecionadas.includes(tag.codigo)}
                  onChange={(checked) =>
                    setValue(
                      'tags_codigos',
                      checked
                        ? [...tagsSelecionadas, tag.codigo]
                        : tagsSelecionadas.filter((c) => c !== tag.codigo),
                    )
                  }
                />
              ))}
            </div>
          </fieldset>
        )}

        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-[var(--color-fg)]">Casos de teste</h3>
            <Button
              type="button"
              variant="secondary"
              className="px-3 py-1 text-xs"
              onClick={() => append({ entrada: '', saida_esperada: '', publico: false })}
            >
              <Plus className="h-3.5 w-3.5" aria-hidden="true" />
              Adicionar caso
            </Button>
          </div>
          {errors.casos?.root && (
            <p role="alert" className="text-xs font-medium text-[var(--color-danger)]">
              {errors.casos.root.message}
            </p>
          )}
          {fields.map((field, index) => (
            <div key={field.id} className="rounded-md border border-[var(--color-border)] p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-medium text-[var(--color-muted)]">Caso {index + 1}</span>
                {fields.length > 1 && (
                  <button
                    type="button"
                    aria-label={`Remover caso ${index + 1}`}
                    onClick={() => remove(index)}
                    className="text-[var(--color-danger)] hover:opacity-75"
                  >
                    <Trash2 className="h-4 w-4" aria-hidden="true" />
                  </button>
                )}
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <InputField label="Entrada" {...register(`casos.${index}.entrada`)} />
                <InputField
                  label="Saída esperada"
                  erro={errors.casos?.[index]?.saida_esperada?.message}
                  {...register(`casos.${index}.saida_esperada`)}
                />
              </div>
              <div className="mt-2">
                <CheckboxField
                  label="Caso público (visível ao aluno)"
                  checked={watch(`casos.${index}.publico`)}
                  onChange={(v) => setValue(`casos.${index}.publico`, v)}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
          <Button type="submit" carregando={isSubmitting}>
            Criar problema
          </Button>
        </div>
      </form>
    </Card>
  )
}
