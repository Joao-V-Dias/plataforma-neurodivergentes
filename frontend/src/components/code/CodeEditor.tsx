import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { useId, useMemo } from 'react'
import { EditorView } from '@codemirror/view'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  label: string
  readOnly?: boolean
}

const TAMANHO_PARA_PX: Record<string, string> = {
  pequeno: '13px',
  medio: '14px',
  grande: '16px',
  extra_grande: '18px',
}

/** Editor de código (CodeMirror 6). Diferente do resto da UI, o tamanho de
 * fonte do editor não segue a variável CSS global `--font-scale` (código
 * precisa de fonte monoespaçada e largura previsível) - em vez disso lemos
 * a preferência de tamanho de fonte diretamente e aplicamos ao próprio
 * CodeMirror, para o editor continuar respeitando a preferência do
 * usuário sem quebrar o alinhamento de colunas do código. */
export function CodeEditor({ value, onChange, label, readOnly }: CodeEditorProps) {
  const { preferencias } = useAccessibility()
  const id = useId()
  const fontSize = TAMANHO_PARA_PX[preferencias.tamanho_fonte] ?? '14px'

  const extensions = useMemo(
    () => [
      python(),
      EditorView.theme({
        '&': { fontSize },
        '.cm-content': { fontFamily: 'ui-monospace, Menlo, Consolas, monospace' },
      }),
    ],
    [fontSize],
  )

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-[var(--color-fg)]">
        {label}
      </label>
      {/* CodeMirror gerencia o próprio foco/teclado internamente; o id vai
          num wrapper acessível via aria-label no lugar de um <label for>
          direto, que o CodeMirror não expõe. */}
      <div
        id={id}
        role="group"
        aria-label={label}
        className="overflow-hidden rounded-md border border-[var(--color-border)]"
      >
        <CodeMirror
          value={value}
          onChange={onChange}
          extensions={extensions}
          readOnly={readOnly}
          height="320px"
          basicSetup={{ tabSize: 4 }}
        />
      </div>
    </div>
  )
}
