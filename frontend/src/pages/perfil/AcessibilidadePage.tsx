import { useState, type FormEvent } from 'react'
import { Card, CardHeader } from '@/components/ui/Card'
import { SwitchField } from '@/components/ui/Checkbox'
import { RadioGroupField } from '@/components/ui/RadioGroup'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import { useToast } from '@/components/ui/useToast'
import { mensagemDeErro } from '@/lib/api/errors'
import type { PreferenciasAcessibilidadeRequest, TamanhoFonte } from '@/lib/api/types'

const OPCOES_TAMANHO: { value: TamanhoFonte; label: string }[] = [
  { value: 'pequeno', label: 'Pequeno' },
  { value: 'medio', label: 'Médio (padrão)' },
  { value: 'grande', label: 'Grande' },
  { value: 'extra_grande', label: 'Extra grande' },
]

export function AcessibilidadePage() {
  const { preferencias, salvarPreferencias, salvando, suportaLeituraEmVoz } = useAccessibility()
  const { notificar } = useToast()
  const [form, setForm] = useState<PreferenciasAcessibilidadeRequest>(preferencias)
  const [erro, setErro] = useState<string | null>(null)

  // As preferências chegam de forma assíncrona (React Query): em vez de um
  // useEffect + setState (que causa uma renderização em cascata extra),
  // ajustamos o rascunho local durante a própria renderização quando o
  // dado do servidor muda - padrão recomendado pela documentação do React
  // para "adjusting state when a prop changes".
  const [preferenciasAnteriores, setPreferenciasAnteriores] = useState(preferencias)
  if (preferenciasAnteriores !== preferencias) {
    setPreferenciasAnteriores(preferencias)
    setForm(preferencias)
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setErro(null)
    try {
      await salvarPreferencias(form)
      notificar({ titulo: 'Preferências salvas', tone: 'success' })
    } catch (erroSalvar) {
      setErro(mensagemDeErro(erroSalvar))
    }
  }

  return (
    <Card className="max-w-xl">
      <CardHeader
        title="Preferências de acessibilidade"
        description="Essas configurações se aplicam a toda a plataforma, em qualquer dispositivo em que você entrar."
      />
      <form className="flex flex-col gap-5" onSubmit={(e) => void onSubmit(e)}>
        {erro && <Alert tone="danger">{erro}</Alert>}

        <RadioGroupField
          label="Tamanho da fonte"
          opcoes={OPCOES_TAMANHO}
          value={form.tamanho_fonte}
          onChange={(v) => setForm((f) => ({ ...f, tamanho_fonte: v as TamanhoFonte }))}
          orientacao="horizontal"
        />

        <SwitchField
          label="Fonte legível"
          descricao="Aumenta o espaçamento entre letras e linhas - ajuda especialmente na leitura com dislexia."
          checked={form.fonte_legivel}
          onChange={(v) => setForm((f) => ({ ...f, fonte_legivel: v }))}
        />

        <SwitchField
          label="Alto contraste"
          descricao="Fundo preto e texto em alto contraste em toda a plataforma."
          checked={form.alto_contraste}
          onChange={(v) => setForm((f) => ({ ...f, alto_contraste: v }))}
        />

        <SwitchField
          label="Redução de estímulos"
          descricao="Remove animações e transições visuais."
          checked={form.reducao_estimulos}
          onChange={(v) => setForm((f) => ({ ...f, reducao_estimulos: v }))}
        />

        <SwitchField
          label="Leitura em voz alta"
          descricao={
            suportaLeituraEmVoz
              ? 'Mostra um botão "ouvir" em enunciados de problema e dicas.'
              : 'Seu navegador não tem suporte a esta funcionalidade.'
          }
          checked={form.leitura_voz_alta}
          onChange={(v) => setForm((f) => ({ ...f, leitura_voz_alta: v }))}
          disabled={!suportaLeituraEmVoz}
        />

        <div className="flex flex-col gap-1.5">
          <label htmlFor="tempo-extra" className="text-sm font-medium text-[var(--color-fg)]">
            Tempo extra: {form.tempo_extra_percentual}%
          </label>
          <input
            id="tempo-extra"
            type="range"
            min={0}
            max={200}
            step={10}
            value={form.tempo_extra_percentual}
            onChange={(e) =>
              setForm((f) => ({ ...f, tempo_extra_percentual: Number(e.target.value) }))
            }
            className="accent-[var(--color-primary)]"
          />
          <p className="text-xs text-[var(--color-muted)]">
            Acrescido a prazos e limites de tempo relacionados à sua conta.
          </p>
        </div>

        <Button type="submit" carregando={salvando} className="mt-2 justify-center">
          Salvar preferências
        </Button>
      </form>
    </Card>
  )
}
