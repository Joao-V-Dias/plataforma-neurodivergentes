import { CheckCircle2, EyeOff, XCircle } from 'lucide-react'
import type { ResultadoCasoResponse } from '@/lib/api/types'
import { cn } from '@/lib/cn'

export function ResultadoCasoCard({ resultado, indice }: { resultado: ResultadoCasoResponse; indice: number }) {
  return (
    <div
      className={cn(
        'rounded-md border p-3 text-sm',
        resultado.passou
          ? 'border-[var(--color-success)] bg-[var(--color-success-bg)]'
          : 'border-[var(--color-danger)] bg-[var(--color-danger-bg)]',
      )}
    >
      <div className="flex items-center gap-2 font-medium">
        {resultado.passou ? (
          <CheckCircle2 className="h-4 w-4 text-[var(--color-success)]" aria-hidden="true" />
        ) : (
          <XCircle className="h-4 w-4 text-[var(--color-danger)]" aria-hidden="true" />
        )}
        <span>
          Caso {indice + 1} · {resultado.passou ? 'Passou' : 'Não passou'}
        </span>
        {!resultado.publico && (
          <span className="ml-auto flex items-center gap-1 text-xs font-normal text-[var(--color-muted)]">
            <EyeOff className="h-3.5 w-3.5" aria-hidden="true" />
            Caso oculto
          </span>
        )}
      </div>

      {resultado.publico ? (
        <dl className="mt-2 grid gap-1.5 font-mono text-xs">
          <div>
            <dt className="inline text-[var(--color-muted)]">Entrada: </dt>
            <dd className="inline">{resultado.entrada || '(vazia)'}</dd>
          </div>
          <div>
            <dt className="inline text-[var(--color-muted)]">Esperado: </dt>
            <dd className="inline">{resultado.saida_esperada}</dd>
          </div>
          <div>
            <dt className="inline text-[var(--color-muted)]">Obtido: </dt>
            <dd className="inline">{resultado.saida_obtida || '(vazio)'}</dd>
          </div>
          {resultado.erro && (
            <div>
              <dt className="inline text-[var(--color-muted)]">Erro: </dt>
              <dd className="inline">{resultado.erro}</dd>
            </div>
          )}
        </dl>
      ) : (
        <p className="mt-1.5 text-xs text-[var(--color-muted)]">
          Detalhes deste caso não são exibidos - apenas se passou ou não.
        </p>
      )}
    </div>
  )
}
