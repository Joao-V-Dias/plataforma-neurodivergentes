import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import * as turmasApi from '@/lib/api/turmas'
import { Card, CardHeader } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { PageSpinner } from '@/components/ui/Spinner'
import { NovaTurmaDialog } from './NovaTurmaDialog'

export function TurmasListPage() {
  const [dialogAberto, setDialogAberto] = useState(false)
  const { data: turmas, isLoading } = useQuery({ queryKey: ['turmas'], queryFn: turmasApi.listarTurmas })

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader
          title="Turmas"
          description="Professores veem suas turmas vinculadas; Coordenadores e Diretores veem todas as turmas da instituição."
          action={
            <Button onClick={() => setDialogAberto(true)}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Nova turma
            </Button>
          }
        />

        {isLoading && <PageSpinner label="Carregando turmas..." />}

        {turmas && turmas.length === 0 && (
          <p className="py-6 text-center text-sm text-[var(--color-muted)]">
            Nenhuma turma cadastrada ainda.
          </p>
        )}

        {turmas && turmas.length > 0 && (
          <ul className="flex flex-col gap-2">
            {turmas.map((turma) => (
              <li key={turma.id}>
                <Link
                  to={`/turmas/${turma.id}`}
                  className="flex items-center justify-between rounded-md border border-[var(--color-border)] px-4 py-3 hover:bg-[var(--color-surface)]"
                >
                  <span>
                    <span className="font-medium text-[var(--color-fg)]">{turma.nome}</span>
                    <span className="ml-2 text-sm text-[var(--color-muted)]">{turma.periodo}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <NovaTurmaDialog open={dialogAberto} onOpenChange={setDialogAberto} />
    </div>
  )
}
