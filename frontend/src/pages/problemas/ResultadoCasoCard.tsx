import { CheckCircle2, EyeOff, XCircle } from 'lucide-react'
import type { ResultadoCasoResponse } from '@/lib/api/types'
import './ResultadoCasoCard.css'

export function ResultadoCasoCard({ resultado, indice }: { resultado: ResultadoCasoResponse; indice: number }) {
  return (
    <div className="resultado-caso" data-passou={resultado.passou}>
      <div className="resultado-caso__cabecalho">
        {resultado.passou ? <CheckCircle2 size={16} className="resultado-caso__icone-ok" /> : <XCircle size={16} className="resultado-caso__icone-erro" />}
        <span>Caso {indice + 1}</span>
        {!resultado.publico && (
          <span className="resultado-caso__oculto">
            <EyeOff size={12} /> oculto
          </span>
        )}
        <span className="resultado-caso__tempo">{resultado.tempo_execucao_ms} ms</span>
      </div>
      {resultado.publico && (
        <dl className="resultado-caso__detalhes">
          {resultado.entrada !== null && (
            <div>
              <dt>Entrada</dt>
              <dd>
                <code>{resultado.entrada || '(vazia)'}</code>
              </dd>
            </div>
          )}
          <div>
            <dt>Esperado</dt>
            <dd>
              <code>{resultado.saida_esperada}</code>
            </dd>
          </div>
          <div>
            <dt>Obtido</dt>
            <dd>
              <code>{resultado.saida_obtida ?? '—'}</code>
            </dd>
          </div>
          {resultado.erro && (
            <div>
              <dt>Erro</dt>
              <dd>
                <code>{resultado.erro}</code>
              </dd>
            </div>
          )}
        </dl>
      )}
    </div>
  )
}
