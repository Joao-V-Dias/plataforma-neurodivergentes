import { python } from '@codemirror/lang-python'
import CodeMirror from '@uiw/react-codemirror'
import { githubDark, githubLight } from '@uiw/codemirror-theme-github'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import './CodeEditor.css'

export function CodeEditor({
  value,
  onChange,
  somenteLeitura,
}: {
  value: string
  onChange: (v: string) => void
  somenteLeitura?: boolean
}) {
  const { tema } = useAccessibility()
  return (
    <div className="code-editor">
      <CodeMirror
        value={value}
        height="24rem"
        theme={tema === 'claro' ? githubLight : githubDark}
        extensions={[python()]}
        onChange={onChange}
        readOnly={somenteLeitura}
        basicSetup={{ tabSize: 4 }}
      />
    </div>
  )
}
