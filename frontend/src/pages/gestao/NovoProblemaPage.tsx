import { useQuery } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Field } from '@/components/ui/Field'
import { Input, Textarea } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { paraErroApi } from '@/lib/api/errors'
import { criarProblema, listarTags } from '@/lib/api/problemas'
import type { CasoTesteInputSchema, NivelDificuldade } from '@/lib/api/types'
import './NovoProblemaPage.css'

function novoCaso(): CasoTesteInputSchema {
  return { entrada: '', saida_esperada: '', publico: true }
}

export function NovoProblemaPage() {
  const navigate = useNavigate()
  const tagsQuery = useQuery({ queryKey: ['tags'], queryFn: listarTags })

  const [titulo, setTitulo] = useState('')
  const [enunciado, setEnunciado] = useState('')
  const [linguagem, setLinguagem] = useState('python')
  const [nivel, setNivel] = useState<NivelDificuldade>('facil')
  const [tagsSelecionadas, setTagsSelecionadas] = useState<string[]>([])
  const [casos, setCasos] = useState<CasoTesteInputSchema[]>([novoCaso()])
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  function atualizarCaso(i: number, patch: Partial<CasoTesteInputSchema>) {
    setCasos((atual) => atual.map((c, idx) => (idx === i ? { ...c, ...patch } : c)))
  }

  async function salvar() {
    setErro(null)
    if (!titulo.trim() || !enunciado.trim() || casos.length === 0) {
      setErro('Preencha título, enunciado e ao menos um caso de teste.')
      return
    }
    if (!casos.some((c) => c.publico)) {
      setErro('Ao menos um caso de teste precisa ser público, para o aluno ver um exemplo.')
      return
    }
    setEnviando(true)
    try {
      const problema = await criarProblema({
        titulo,
        enunciado,
        linguagem,
        nivel_dificuldade: nivel,
        tags_codigos: tagsSelecionadas,
        casos,
      })
      navigate(`/gestao/problemas/${problema.id}`, { replace: true })
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="novo-problema">
      <header className="gestao-topo">
        <div>
          <h1>Novo problema</h1>
          <p>Defina o enunciado e os casos de teste públicos e ocultos.</p>
        </div>
      </header>

      <div className="novo-problema__form">
        <Field label="Título" htmlFor="titulo" obrigatorio>
          <Input id="titulo" value={titulo} onChange={(e) => setTitulo(e.target.value)} />
        </Field>
        <Field label="Enunciado" htmlFor="enunciado" obrigatorio>
          <Textarea id="enunciado" rows={6} value={enunciado} onChange={(e) => setEnunciado(e.target.value)} />
        </Field>
        <div className="novo-problema__linha">
          <Field label="Linguagem" htmlFor="linguagem" obrigatorio>
            <Input id="linguagem" value={linguagem} onChange={(e) => setLinguagem(e.target.value)} />
          </Field>
          <Field label="Nível de dificuldade" htmlFor="nivel" obrigatorio>
            <Select
              id="nivel"
              value={nivel}
              onValueChange={(v) => setNivel(v as NivelDificuldade)}
              opcoes={[
                { value: 'facil', label: 'Fácil' },
                { value: 'medio', label: 'Médio' },
                { value: 'dificil', label: 'Difícil' },
              ]}
            />
          </Field>
        </div>

        {tagsQuery.data && tagsQuery.data.length > 0 && (
          <div>
            <p className="field__label">Tags</p>
            <div className="novo-problema__tags">
              {tagsQuery.data.map((t) => (
                <Checkbox
                  key={t.id}
                  id={`tag-${t.codigo}`}
                  checked={tagsSelecionadas.includes(t.codigo)}
                  onCheckedChange={(v) =>
                    setTagsSelecionadas((atual) => (v ? [...atual, t.codigo] : atual.filter((x) => x !== t.codigo)))
                  }
                  label={t.nome}
                />
              ))}
            </div>
          </div>
        )}

        <div className="novo-problema__casos">
          <div className="novo-problema__casos-cabecalho">
            <p className="field__label">Casos de teste</p>
            <Button variante="fantasma" tamanho="sm" onClick={() => setCasos((atual) => [...atual, novoCaso()])}>
              <Plus size={14} /> Adicionar caso
            </Button>
          </div>
          {casos.map((caso, i) => (
            <div key={i} className="novo-problema__caso">
              <div className="novo-problema__caso-linha">
                <Field label="Entrada" htmlFor={`entrada-${i}`}>
                  <Textarea id={`entrada-${i}`} rows={2} value={caso.entrada} onChange={(e) => atualizarCaso(i, { entrada: e.target.value })} />
                </Field>
                <Field label="Saída esperada" htmlFor={`saida-${i}`} obrigatorio>
                  <Textarea
                    id={`saida-${i}`}
                    rows={2}
                    value={caso.saida_esperada}
                    onChange={(e) => atualizarCaso(i, { saida_esperada: e.target.value })}
                  />
                </Field>
              </div>
              <div className="novo-problema__caso-rodape">
                <Checkbox
                  id={`publico-${i}`}
                  checked={caso.publico}
                  onCheckedChange={(v) => atualizarCaso(i, { publico: v })}
                  label="Caso público (aluno vê como exemplo)"
                />
                {casos.length > 1 && (
                  <button
                    type="button"
                    className="novo-problema__remover"
                    onClick={() => setCasos((atual) => atual.filter((_, idx) => idx !== i))}
                    aria-label="Remover caso de teste"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {erro && <p className="field__erro" role="alert">{erro}</p>}
        <Button carregando={enviando} onClick={() => void salvar()}>
          Criar problema
        </Button>
      </div>
    </div>
  )
}
