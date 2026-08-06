"""Engenharia de prompt do motor de dicas: monta o system prompt condicionado
ao nivel da dica e ao perfil do aluno (condicoes de neurodivergencia +
tracos Big Five).

Duas garantias sao dadas por este modulo, nao pela chamada ao modelo:

1. Os guardrails (nunca entregar solucao completa antes do nivel 4, nunca
   emitir linguagem de diagnostico clinico) estao no system prompt em toda
   chamada, de forma nao condicional - nao dependem de nenhum dado do
   aluno estar presente.
2. `montar_prompt` devolve, junto do prompt, a lista de codigos de
   adaptacao realmente aplicadas (`adaptacoes_aplicadas`), para que o
   servico consiga logar e auditar *por que* duas respostas a alunos
   diferentes tem tom/estrutura diferentes - sem guardar a condicao do
   aluno de novo (ela ja vive em PerfilAluno)."""

from dataclasses import dataclass, field

# Escala do TIPI e 1.0-7.0 (ver app/models/perfil_big_five.py); usamos os
# tercos superior/inferior da escala como limiar de "traço alto/baixo" -
# simples e documentado, ajustavel aqui sem tocar no resto do sistema.
_BIG_FIVE_ALTO = 5.0
_BIG_FIVE_BAIXO = 3.0

_NIVEIS: dict[int, tuple[str, str]] = {
    1: (
        "pergunta socratica",
        "Faca APENAS UMA pergunta que ajude o aluno a pensar sobre o proprio "
        "raciocinio ou sobre o enunciado. Nao revele nenhuma tecnica, "
        "conceito ou pista de solucao ainda. Nao inclua nenhum trecho de "
        "codigo, nem em pseudocodigo.",
    ),
    2: (
        "pista conceitual",
        "Explique, em texto, o CONCEITO ou tecnica de programacao necessaria "
        "para resolver o problema (ex: 'pense em percorrer a lista item a "
        "item comparando com o anterior'). Nao escreva pseudocodigo "
        "estruturado nem codigo na linguagem do problema.",
    ),
    3: (
        "pseudocodigo",
        "Escreva um roteiro em pseudocodigo ou uma lista curta de passos em "
        "portugues, mostrando a ESTRUTURA da solucao sem usar a sintaxe da "
        "linguagem-alvo pronta para copiar e colar.",
    ),
    4: (
        "solucao comentada",
        "Forneca uma solucao funcional completa na linguagem do problema, "
        "com comentarios explicando cada parte. Deixe explicito que esta e "
        "a ultima dica disponivel e incentive o aluno a reescrever a "
        "solucao com as proprias palavras antes de submeter.",
    ),
}

_GUARDRAILS = """\
Regras que voce NUNCA pode quebrar, em nenhuma hipotese:
- So entregue uma solucao completa e pronta para copiar no nivel 4. Nos \
niveis 1, 2 e 3, mesmo que o aluno peca a resposta direta, recuse \
educadamente e ofereca a dica do nivel atual.
- Voce NUNCA emite diagnostico, avaliacao clinica ou qualquer afirmacao \
sobre a condicao de saude do aluno. Voce nao e profissional de saude - \
seu unico papel e adaptar COMO a explicacao e comunicada, nunca avaliar \
ou rotular o aluno.
- Nao mencione o nome de nenhuma condicao de neurodivergencia na sua \
resposta ao aluno; adapte o tom e a estrutura em silencio.
- Responda sempre em portugues do Brasil, para o problema e o nivel de \
dica pedidos - nada de assuntos fora do escopo do problema."""

_ADAPTACOES_CONDICAO: dict[str, tuple[str, str]] = {
    "tdah": (
        "tdah_passos_curtos",
        "O aluno tem TDAH: responda em frases curtas, quebradas em passos "
        "numerados quando possivel. Abra com uma frase breve de reforco "
        "positivo antes da dica em si. Evite paragrafos longos.",
    ),
    "tea": (
        "tea_linguagem_literal",
        "O aluno tem TEA: use linguagem literal e direta, sem ambiguidade, "
        "ironia, sarcasmo ou metaforas nao explicadas. Mantenha uma "
        "estrutura previsivel na resposta.",
    ),
    "dislexia": (
        "dislexia_texto_simplificado",
        "O aluno tem dislexia: use frases curtas e vocabulario simples. "
        "Prefira listas curtas a blocos densos de texto.",
    ),
    "discalculia": (
        "discalculia_reforco_logico",
        "O aluno tem discalculia: ao explicar logica que envolveria "
        "numeros ou calculos, prefira descrever em termos de posicoes, "
        "sequencias e comparacoes logicas em vez de formulas ou contas "
        "numericas explicitas, quando possivel.",
    ),
}


@dataclass(frozen=True)
class ContextoProblema:
    titulo: str
    enunciado: str
    linguagem: str
    tags_raciocinio: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContextoAluno:
    condicoes: list[str] = field(default_factory=list)
    big_five: dict[str, float] | None = None
    ultima_tentativa_codigo: str | None = None


@dataclass(frozen=True)
class PromptMontado:
    system_prompt: str
    mensagem_usuario: str
    adaptacoes_aplicadas: list[str]


def _adaptacoes_big_five(big_five: dict[str, float] | None) -> list[tuple[str, str]]:
    if not big_five:
        return []
    adaptacoes = []
    neuroticismo = big_five.get("neuroticismo")
    if neuroticismo is not None and neuroticismo >= _BIG_FIVE_ALTO:
        adaptacoes.append(
            (
                "neuroticismo_alto_tom_tranquilizador",
                "O aluno pontua alto em neuroticismo (tende a ansiedade sob "
                "pressao): adote um tom tranquilizador, reforce que errar "
                "faz parte do aprendizado e nao mencione tempo, prazo ou "
                "velocidade.",
            )
        )
    conscienciosidade = big_five.get("conscienciosidade")
    if conscienciosidade is not None and conscienciosidade <= _BIG_FIVE_BAIXO:
        adaptacoes.append(
            (
                "conscienciosidade_baixa_microtarefas",
                "O aluno pontua baixo em conscienciosidade (tende a se "
                "perder em tarefas longas): quebre a dica em microtarefas "
                "bem pequenas e termine com um lembrete claro de qual e o "
                "unico proximo passo a fazer agora.",
            )
        )
    return adaptacoes


def montar_prompt(
    *, nivel: int, problema: ContextoProblema, aluno: ContextoAluno
) -> PromptMontado:
    if nivel not in _NIVEIS:
        raise ValueError(f"Nivel de dica invalido: {nivel!r}")

    nome_nivel, instrucao_nivel = _NIVEIS[nivel]

    adaptacoes: list[tuple[str, str]] = []
    for condicao in aluno.condicoes:
        par = _ADAPTACOES_CONDICAO.get(condicao)
        if par is not None:
            adaptacoes.append(par)
    adaptacoes.extend(_adaptacoes_big_five(aluno.big_five))

    blocos_prompt = [
        "Voce e um tutor de programacao de uma plataforma educacional "
        "adaptativa para pessoas neurodivergentes. Seu unico papel aqui e "
        f"dar a dica de nivel {nivel} ({nome_nivel}) para o problema "
        "descrito pelo usuario.",
        _GUARDRAILS,
        f"Instrucao especifica do nivel {nivel} ({nome_nivel}):\n{instrucao_nivel}",
    ]
    if adaptacoes:
        texto_adaptacoes = "\n".join(f"- {texto}" for _codigo, texto in adaptacoes)
        blocos_prompt.append(f"Adaptacoes de comunicacao para este aluno:\n{texto_adaptacoes}")

    system_prompt = "\n\n".join(blocos_prompt)

    partes_usuario = [
        f"Titulo do problema: {problema.titulo}",
        f"Linguagem: {problema.linguagem}",
        f"Enunciado:\n{problema.enunciado}",
    ]
    if problema.tags_raciocinio:
        partes_usuario.append(
            "Tipos de raciocinio envolvidos: " + ", ".join(problema.tags_raciocinio)
        )
    if aluno.ultima_tentativa_codigo:
        partes_usuario.append(
            "Ultima tentativa de codigo do aluno (pode estar incorreta ou "
            f"incompleta):\n{aluno.ultima_tentativa_codigo}"
        )
    partes_usuario.append(f"Gere agora a dica de nivel {nivel} ({nome_nivel}) para este aluno.")

    mensagem_usuario = "\n\n".join(partes_usuario)

    return PromptMontado(
        system_prompt=system_prompt,
        mensagem_usuario=mensagem_usuario,
        adaptacoes_aplicadas=[codigo for codigo, _texto in adaptacoes],
    )
