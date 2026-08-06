"""Testes puros da engenharia de prompt (app/ai/prompts.py) - sem banco,
sem rede, sem mock: a montagem de prompt e uma funcao determinística."""

import pytest

from app.ai.prompts import ContextoAluno, ContextoProblema, montar_prompt

_PROBLEMA = ContextoProblema(
    titulo="Fibonacci", enunciado="Imprima o N-esimo termo.", linguagem="python"
)


@pytest.mark.parametrize("nivel", [1, 2, 3, 4])
def test_guardrails_sempre_presentes_independente_do_nivel(nivel: int) -> None:
    prompt = montar_prompt(nivel=nivel, problema=_PROBLEMA, aluno=ContextoAluno())
    assert "So entregue uma solucao completa" in prompt.system_prompt
    assert "diagnostico" in prompt.system_prompt.lower()
    assert "nao e profissional de saude" in prompt.system_prompt


def test_nivel_invalido_levanta_erro() -> None:
    with pytest.raises(ValueError):
        montar_prompt(nivel=5, problema=_PROBLEMA, aluno=ContextoAluno())
    with pytest.raises(ValueError):
        montar_prompt(nivel=0, problema=_PROBLEMA, aluno=ContextoAluno())


def test_nivel_1_nao_pede_pseudocodigo_nem_solucao() -> None:
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=ContextoAluno())
    assert "pergunta socratica" in prompt.system_prompt.lower()
    assert "solucao funcional completa" not in prompt.system_prompt


def test_nivel_4_pede_solucao_comentada() -> None:
    prompt = montar_prompt(nivel=4, problema=_PROBLEMA, aluno=ContextoAluno())
    assert "solucao funcional completa" in prompt.system_prompt


def test_sem_perfil_nenhuma_adaptacao_aplicada() -> None:
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=ContextoAluno())
    assert prompt.adaptacoes_aplicadas == []


def test_multiplas_condicoes_acumulam_adaptacoes() -> None:
    aluno = ContextoAluno(condicoes=["tdah", "discalculia"])
    prompt = montar_prompt(nivel=2, problema=_PROBLEMA, aluno=aluno)
    assert prompt.adaptacoes_aplicadas == ["tdah_passos_curtos", "discalculia_reforco_logico"]


def test_condicao_desconhecida_e_ignorada_sem_erro() -> None:
    aluno = ContextoAluno(condicoes=["disgrafia"])
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=aluno)
    assert prompt.adaptacoes_aplicadas == []


def test_big_five_conscienciosidade_baixa_pede_microtarefas() -> None:
    aluno = ContextoAluno(big_five={"conscienciosidade": 2.0})
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=aluno)
    assert prompt.adaptacoes_aplicadas == ["conscienciosidade_baixa_microtarefas"]
    assert "microtarefas" in prompt.system_prompt


def test_big_five_traco_neutro_nao_ativa_nenhuma_adaptacao() -> None:
    aluno = ContextoAluno(big_five={"neuroticismo": 4.0, "conscienciosidade": 4.0})
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=aluno)
    assert prompt.adaptacoes_aplicadas == []


def test_ultima_tentativa_e_incluida_na_mensagem_do_usuario() -> None:
    aluno = ContextoAluno(ultima_tentativa_codigo="print('oi')")
    prompt = montar_prompt(nivel=1, problema=_PROBLEMA, aluno=aluno)
    assert "print('oi')" in prompt.mensagem_usuario


def test_tags_de_raciocinio_sao_incluidas_na_mensagem_do_usuario() -> None:
    problema = ContextoProblema(
        titulo="X", enunciado="Y", linguagem="python", tags_raciocinio=["logica sequencial"]
    )
    prompt = montar_prompt(nivel=1, problema=problema, aluno=ContextoAluno())
    assert "logica sequencial" in prompt.mensagem_usuario
