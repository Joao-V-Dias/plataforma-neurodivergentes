import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import * as problemasApi from '@/lib/api/problemas'
import { NIVEL_DIFICULDADE_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ButtonLink } from '@/components/ui/Button'
import { PageSpinner } from '@/components/ui/Spinner'

const NIVEL_TONE = { facil: 'success', medio: 'warning', dificil: 'danger' } as const

export function ProblemasListPage() {
  const { data: problemas, isLoading } = useQuery({
    queryKey: ['problemas'],
    queryFn: problemasApi.listarProblemas,
  })

  return (
    <Card>
      <CardHeader
        title="Banco de problemas"
        description="Problemas cadastrados pela sua instituição."
        action={
          <ButtonLink to="/problemas/novo">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Novo problema
          </ButtonLink>
        }
      />
      {isLoading && <PageSpinner label="Carregando problemas..." />}
      {problemas && problemas.length === 0 && (
        <p className="py-6 text-center text-sm text-[var(--color-muted)]">
          Nenhum problema cadastrado ainda.
        </p>
      )}
      {problemas && problemas.length > 0 && (
        <ul className="flex flex-col gap-2">
          {problemas.map((p) => (
            <li key={p.id}>
              <Link
                to={`/problemas/${p.id}`}
                className="flex items-center justify-between gap-3 rounded-md border border-[var(--color-border)] px-4 py-3 hover:bg-[var(--color-surface)]"
              >
                <div>
                  <p className="font-medium text-[var(--color-fg)]">{p.titulo}</p>
                  <div className="mt-1 flex flex-wrap gap-1.5">
                    {p.tags.map((tag) => (
                      <Badge key={tag.id} tone="neutral">
                        {tag.nome}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Badge tone={NIVEL_TONE[p.nivel_dificuldade]}>
                  {NIVEL_DIFICULDADE_LABEL[p.nivel_dificuldade]}
                </Badge>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
