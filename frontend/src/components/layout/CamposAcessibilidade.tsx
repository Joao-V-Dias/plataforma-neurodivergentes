import { Moon, Sun, Type } from 'lucide-react'
import { Checkbox } from '@/components/ui/Checkbox'
import { RadioGroup } from '@/components/ui/RadioGroup'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import './CamposAcessibilidade.css'

export function CamposAcessibilidade() {
  const { preferencias, tema, atualizar, alternarTema, salvando } = useAccessibility()

  return (
    <div className="a11y-painel">
      <section className="a11y-painel__secao">
        <p className="a11y-painel__rotulo">Tema</p>
        <button type="button" className="a11y-painel__tema" onClick={alternarTema}>
          {tema === 'escuro' ? <Sun size={15} /> : <Moon size={15} />}
          Alternar para tema {tema === 'escuro' ? 'claro' : 'escuro'}
        </button>
      </section>

      <section className="a11y-painel__secao">
        <p className="a11y-painel__rotulo">
          <Type size={14} /> Tamanho da fonte
        </p>
        <RadioGroup
          name="tamanho_fonte"
          orientacao="horizontal"
          value={preferencias.tamanho_fonte}
          onValueChange={(v) => atualizar({ tamanho_fonte: v as typeof preferencias.tamanho_fonte })}
          opcoes={[
            { value: 'pequeno', label: 'Pequena' },
            { value: 'medio', label: 'Média' },
            { value: 'grande', label: 'Grande' },
            { value: 'extra_grande', label: 'Extra grande' },
          ]}
        />
      </section>

      <section className="a11y-painel__secao a11y-painel__lista">
        <Checkbox
          id="a11y-alto-contraste"
          checked={preferencias.alto_contraste}
          onCheckedChange={(v) => atualizar({ alto_contraste: v })}
          label="Alto contraste"
        />
        <Checkbox
          id="a11y-fonte-legivel"
          checked={preferencias.fonte_legivel}
          onCheckedChange={(v) => atualizar({ fonte_legivel: v })}
          label="Fonte com espaçamento ampliado (apoio à leitura)"
        />
        <Checkbox
          id="a11y-leitura-voz"
          checked={preferencias.leitura_voz_alta}
          onCheckedChange={(v) => atualizar({ leitura_voz_alta: v })}
          label="Habilitar botão de leitura em voz alta nos textos"
        />
        <Checkbox
          id="a11y-reducao-estimulos"
          checked={preferencias.reducao_estimulos}
          onCheckedChange={(v) => atualizar({ reducao_estimulos: v })}
          label="Reduzir animações e estímulos visuais"
        />
      </section>

      <section className="a11y-painel__secao">
        <p className="a11y-painel__rotulo">
          Tempo extra em exercícios: {preferencias.tempo_extra_percentual}%
        </p>
        <input
          type="range"
          min={0}
          max={200}
          step={10}
          value={preferencias.tempo_extra_percentual}
          onChange={(e) => atualizar({ tempo_extra_percentual: Number(e.target.value) })}
          aria-label="Percentual de tempo extra em exercícios cronometrados"
        />
      </section>

      {salvando && <p className="a11y-painel__status">Salvando…</p>}
    </div>
  )
}
