import { Info } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Checkbox } from '@/components/ui/Checkbox'
import { Textarea } from '@/components/ui/Input'
import './AgendaPage.css'

interface TarefaLocal {
  id: string
  texto: string
  feita: boolean
}

const CHAVE_TAREFAS = 'pna.agenda.checklist'
const CHAVE_DIARIO = 'pna.agenda.diario'

function tarefasIniciais(): TarefaLocal[] {
  try {
    const salvo = localStorage.getItem(CHAVE_TAREFAS)
    if (salvo) return JSON.parse(salvo) as TarefaLocal[]
  } catch {
    // ignora storage corrompido
  }
  return [
    { id: '1', texto: 'Revisar o problema de hoje antes de começar', feita: false },
    { id: '2', texto: 'Fazer uma pausa a cada 25 minutos', feita: false },
  ]
}

/** Mockup: organizador de tarefas e diário de bordo (docs/prompt-redesign-frontend.md
 * §3.5). O backend ainda não expõe uma rota de agenda/diário — os dados
 * aqui ficam só no navegador (localStorage), não sincronizam entre
 * dispositivos nem chegam ao professor. TODO(backend): endpoint de agenda
 * pessoal e de diário de bordo (com opção de compartilhamento). */
export function AgendaPage() {
  const [tarefas, setTarefas] = useState<TarefaLocal[]>(tarefasIniciais)
  const [novaTarefa, setNovaTarefa] = useState('')
  const [diario, setDiario] = useState(() => localStorage.getItem(CHAVE_DIARIO) ?? '')
  const [compartilhar, setCompartilhar] = useState(false)

  useEffect(() => {
    localStorage.setItem(CHAVE_TAREFAS, JSON.stringify(tarefas))
  }, [tarefas])

  useEffect(() => {
    const id = setTimeout(() => localStorage.setItem(CHAVE_DIARIO, diario), 400)
    return () => clearTimeout(id)
  }, [diario])

  function adicionarTarefa() {
    if (!novaTarefa.trim()) return
    setTarefas((atual) => [...atual, { id: crypto.randomUUID(), texto: novaTarefa.trim(), feita: false }])
    setNovaTarefa('')
  }

  return (
    <div className="agenda">
      <h1>Agenda e diário de bordo</h1>
      <p className="agenda__aviso">
        <Info size={14} />
        Pré-visualização local: nada aqui é enviado ao professor ainda. Prazos de problemas
        vinculados à turma aparecerão automaticamente aqui quando o backend expuser essa rota.
      </p>

      <section className="agenda__secao">
        <h2>Checklist de hoje</h2>
        <ul className="agenda__checklist">
          {tarefas.map((t) => (
            <li key={t.id}>
              <Checkbox
                id={`tarefa-${t.id}`}
                checked={t.feita}
                onCheckedChange={(v) =>
                  setTarefas((atual) => atual.map((x) => (x.id === t.id ? { ...x, feita: v } : x)))
                }
                label={t.texto}
              />
            </li>
          ))}
        </ul>
        <div className="agenda__nova-tarefa">
          <input
            className="input"
            value={novaTarefa}
            onChange={(e) => setNovaTarefa(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && adicionarTarefa()}
            placeholder="Adicionar item ao checklist"
            aria-label="Nova tarefa"
          />
        </div>
      </section>

      <section className="agenda__secao">
        <h2>Diário de bordo</h2>
        <p className="agenda__descricao">
          Um espaço para anotar como foi seu estudo hoje — o que funcionou, o que travou. Você
          decide se compartilha com o professor.
        </p>
        <Textarea
          value={diario}
          onChange={(e) => setDiario(e.target.value)}
          placeholder="Como foi resolver os problemas de hoje?"
          rows={6}
        />
        <Checkbox
          id="compartilhar-diario"
          checked={compartilhar}
          onCheckedChange={setCompartilhar}
          label="Compartilhar esta entrada com meu professor"
        />
      </section>
    </div>
  )
}
