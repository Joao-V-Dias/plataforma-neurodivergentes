import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { OnboardingLayout } from './OnboardingLayout'
import { Avatar } from '@/components/ui/Avatar'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Field } from '@/components/ui/Field'
import { Input } from '@/components/ui/Input'
import { RadioGroup } from '@/components/ui/RadioGroup'
import { Textarea } from '@/components/ui/Input'
import { atualizarMeuAvatar } from '@/lib/api/gamificacao'
import { paraErroApi } from '@/lib/api/errors'
import { enviarBigFive, listarCondicoes, obterQuestionarioBigFive, registrarPerfilAluno } from '@/lib/api/perfis'
import { AVATARES, AVATAR_LABEL, type AvatarCodigo } from '@/lib/api/types'
import { useAccessibility } from '@/lib/accessibility/useAccessibility'
import { useAuth } from '@/lib/auth/useAuth'
import { toast } from '@/components/ui/useToast'
import './OnboardingPage.css'

const ESCALA = [1, 2, 3, 4, 5, 6, 7].map((n) => ({ value: String(n), label: String(n) }))

export function OnboardingPage() {
  const { usuario } = useAuth()
  const { preferencias, atualizar: salvarPreferencias } = useAccessibility()
  const navigate = useNavigate()

  const [etapa, setEtapa] = useState(0)
  const [processando, setProcessando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  const [consentimento, setConsentimento] = useState(false)
  const [condicoes, setCondicoes] = useState<string[]>([])
  const [observacoes, setObservacoes] = useState('')
  const [respostas, setRespostas] = useState<number[]>(Array(10).fill(4))
  const [prefsLocais, setPrefsLocais] = useState(preferencias)
  const [avatarCodigo, setAvatarCodigo] = useState<AvatarCodigo | null>(null)
  const [apelido, setApelido] = useState('')

  const { data: listaCondicoes } = useQuery({ queryKey: ['condicoes'], queryFn: listarCondicoes })
  const { data: questionario } = useQuery({
    queryKey: ['big-five-questionario'],
    queryFn: obterQuestionarioBigFive,
  })

  if (!usuario) return null

  async function avancar(acao: () => Promise<void>) {
    setErro(null)
    setProcessando(true)
    try {
      await acao()
      setEtapa((e) => e + 1)
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setProcessando(false)
    }
  }

  async function concluir() {
    setErro(null)
    setProcessando(true)
    try {
      await atualizarMeuAvatar({ apelido: apelido || null, avatar_codigo: avatarCodigo })
      toast({ tipo: 'sucesso', titulo: 'Perfil configurado', descricao: 'Bem-vindo(a) à plataforma.' })
      navigate('/', { replace: true })
    } catch (e) {
      setErro(paraErroApi(e).message)
    } finally {
      setProcessando(false)
    }
  }

  return (
    <OnboardingLayout etapa={etapa}>
      {etapa === 0 && (
        <>
          <h1 className="onboarding__titulo">Consentimento</h1>
          <p className="onboarding__subtitulo">
            Nas próximas telas, perguntamos sobre condições de neurodivergência para adaptar sua
            experiência de estudo. Este é um dado sensível de saúde — informar é opcional e você
            pode revisar ou remover essa informação depois.
          </p>
          <div className="onboarding__corpo">
            <Checkbox
              id="consentimento"
              checked={consentimento}
              onCheckedChange={setConsentimento}
              label="Entendo e aceito que essas informações sejam usadas para adaptar meu ensino."
            />
          </div>
          <div className="onboarding__acoes">
            <span />
            <Button disabled={!consentimento} onClick={() => setEtapa(1)}>
              Continuar
            </Button>
          </div>
        </>
      )}

      {etapa === 1 && (
        <>
          <h1 className="onboarding__titulo">Seu perfil</h1>
          <p className="onboarding__subtitulo">
            Selecione o que se aplica a você, se quiser. Deixar em branco não impede seu acesso.
          </p>
          <div className="onboarding__corpo">
            <div className="onboarding__condicoes">
              {(listaCondicoes ?? []).map((c) => (
                <Checkbox
                  key={c.id}
                  id={`cond-${c.codigo}`}
                  checked={condicoes.includes(c.codigo)}
                  onCheckedChange={(v) =>
                    setCondicoes((atual) => (v ? [...atual, c.codigo] : atual.filter((x) => x !== c.codigo)))
                  }
                  label={c.nome}
                />
              ))}
            </div>
            <Field label="Observações (opcional)" htmlFor="observacoes">
              <Textarea
                id="observacoes"
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                maxLength={2000}
                placeholder="Algo mais que gostaria de contar sobre como você aprende melhor?"
              />
            </Field>
            {erro && <p className="field__erro" role="alert">{erro}</p>}
          </div>
          <div className="onboarding__acoes">
            <Button variante="fantasma" onClick={() => setEtapa(0)}>
              Voltar
            </Button>
            <Button
              carregando={processando}
              onClick={() =>
                avancar(async () => {
                  await registrarPerfilAluno(usuario.id, {
                    condicoes_codigos: condicoes,
                    observacoes: observacoes || null,
                    aceite_consentimento: consentimento,
                  })
                })
              }
            >
              Continuar
            </Button>
          </div>
        </>
      )}

      {etapa === 2 && (
        <>
          <h1 className="onboarding__titulo">Estilo pessoal</h1>
          <p className="onboarding__subtitulo">
            10 afirmações rápidas, sem resposta certa ou errada — ajudam a calibrar o ritmo do
            conteúdo. Escala de 1 (discordo totalmente) a 7 (concordo totalmente).
          </p>
          <div className="onboarding__corpo onboarding__bigfive">
            {(questionario ?? []).map((q, i) => (
              <div key={q.ordem} className="onboarding__questao">
                <p>{q.texto}</p>
                <RadioGroup
                  name={`q-${q.ordem}`}
                  orientacao="horizontal"
                  value={String(respostas[i])}
                  onValueChange={(v) =>
                    setRespostas((atual) => atual.map((r, idx) => (idx === i ? Number(v) : r)))
                  }
                  opcoes={ESCALA}
                />
              </div>
            ))}
            {erro && <p className="field__erro" role="alert">{erro}</p>}
          </div>
          <div className="onboarding__acoes">
            <Button variante="fantasma" onClick={() => setEtapa(1)}>
              Voltar
            </Button>
            <Button
              carregando={processando}
              disabled={!questionario}
              onClick={() => avancar(async () => { await enviarBigFive({ respostas }) })}
            >
              Continuar
            </Button>
          </div>
        </>
      )}

      {etapa === 3 && (
        <>
          <h1 className="onboarding__titulo">Acessibilidade</h1>
          <p className="onboarding__subtitulo">
            Ajuste como o conteúdo aparece para você. Pode ser mudado a qualquer momento pelo ícone
            de acessibilidade no topo da tela.
          </p>
          <div className="onboarding__corpo">
            <Field label="Tamanho da fonte" htmlFor="tamanho_fonte">
              <RadioGroup
                name="tamanho_fonte"
                orientacao="horizontal"
                value={prefsLocais.tamanho_fonte}
                onValueChange={(v) =>
                  setPrefsLocais((p) => ({ ...p, tamanho_fonte: v as typeof p.tamanho_fonte }))
                }
                opcoes={[
                  { value: 'pequeno', label: 'Pequena' },
                  { value: 'medio', label: 'Média' },
                  { value: 'grande', label: 'Grande' },
                  { value: 'extra_grande', label: 'Extra grande' },
                ]}
              />
            </Field>
            <Checkbox
              id="alto_contraste"
              checked={prefsLocais.alto_contraste}
              onCheckedChange={(v) => setPrefsLocais((p) => ({ ...p, alto_contraste: v }))}
              label="Alto contraste"
            />
            <Checkbox
              id="fonte_legivel"
              checked={prefsLocais.fonte_legivel}
              onCheckedChange={(v) => setPrefsLocais((p) => ({ ...p, fonte_legivel: v }))}
              label="Fonte com espaçamento ampliado"
            />
            <Checkbox
              id="leitura_voz_alta"
              checked={prefsLocais.leitura_voz_alta}
              onCheckedChange={(v) => setPrefsLocais((p) => ({ ...p, leitura_voz_alta: v }))}
              label="Habilitar leitura em voz alta nos textos"
            />
            <Checkbox
              id="reducao_estimulos"
              checked={prefsLocais.reducao_estimulos}
              onCheckedChange={(v) => setPrefsLocais((p) => ({ ...p, reducao_estimulos: v }))}
              label="Reduzir animações e estímulos visuais"
            />
            {erro && <p className="field__erro" role="alert">{erro}</p>}
          </div>
          <div className="onboarding__acoes">
            <Button variante="fantasma" onClick={() => setEtapa(2)}>
              Voltar
            </Button>
            <Button carregando={processando} onClick={() => avancar(async () => { await salvarPreferencias(prefsLocais) })}>
              Continuar
            </Button>
          </div>
        </>
      )}

      {etapa === 4 && (
        <>
          <h1 className="onboarding__titulo">Avatar e apelido</h1>
          <p className="onboarding__subtitulo">
            Escolha como quer ser identificado pelos colegas de turma. Isso substitui seu nome nos
            rankings e no mapa da disciplina.
          </p>
          <div className="onboarding__corpo">
            <Field label="Apelido (opcional)" htmlFor="apelido">
              <Input
                id="apelido"
                value={apelido}
                maxLength={40}
                onChange={(e) => setApelido(e.target.value)}
                placeholder={usuario.nome.split(' ')[0]}
              />
            </Field>
            <div className="onboarding__avatares">
              {AVATARES.map((codigo) => (
                <button
                  type="button"
                  key={codigo}
                  className="onboarding__avatar-opcao"
                  data-selecionado={avatarCodigo === codigo}
                  onClick={() => setAvatarCodigo(codigo)}
                >
                  <Avatar codigo={codigo} tamanho={44} />
                  <span>{AVATAR_LABEL[codigo]}</span>
                </button>
              ))}
            </div>
            {erro && <p className="field__erro" role="alert">{erro}</p>}
          </div>
          <div className="onboarding__acoes">
            <Button variante="fantasma" onClick={() => setEtapa(3)}>
              Voltar
            </Button>
            <Button carregando={processando} onClick={() => void concluir()}>
              Concluir
            </Button>
          </div>
        </>
      )}
    </OnboardingLayout>
  )
}
