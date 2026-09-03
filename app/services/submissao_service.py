"""Orquestra a correcao de uma submissao: roda o codigo do aluno no
sandbox (app/sandbox/executor.py) contra cada caso de teste do problema,
compara a saida e grava o resultado. Nunca reexecuta uma submissao ja
gravada - cada tentativa e uma nova linha, preservando o historico
completo exigido pelo escopo."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problema import CasoTeste, Problema
from app.models.submissao import StatusSubmissao, Submissao, SubmissaoResultado
from app.models.usuario import Usuario
from app.repositories import problema_repository, submissao_repository
from app.sandbox.executor import StatusExecucao, executar
from app.services import audit, dica_service, emblema_service, pontuacao_service

# Prioridade de agravamento: a submissao herda o pior status dentre todos
# os casos de teste (ex: um caso com erro_interno "contamina" a submissao
# inteira, mesmo que os outros casos tenham passado).
_PRIORIDADE_STATUS: dict[StatusSubmissao, int] = {
    StatusSubmissao.ACEITO: 0,
    StatusSubmissao.REPROVADO: 1,
    StatusSubmissao.ERRO_EXECUCAO: 2,
    StatusSubmissao.TEMPO_EXCEDIDO: 3,
    StatusSubmissao.ERRO_INTERNO: 4,
}


@dataclass(frozen=True)
class SubmissaoDetalhada:
    submissao: Submissao
    resultados: Sequence[SubmissaoResultado]
    casos_por_id: dict[uuid.UUID, CasoTeste]


def _status_do_caso(status_execucao: StatusExecucao, passou: bool) -> StatusSubmissao:
    if status_execucao == StatusExecucao.TEMPO_EXCEDIDO:
        return StatusSubmissao.TEMPO_EXCEDIDO
    if status_execucao == StatusExecucao.ERRO_INTERNO:
        return StatusSubmissao.ERRO_INTERNO
    if status_execucao == StatusExecucao.ERRO_EXECUCAO:
        return StatusSubmissao.ERRO_EXECUCAO
    return StatusSubmissao.ACEITO if passou else StatusSubmissao.REPROVADO


async def submeter(
    db: AsyncSession,
    *,
    aluno: Usuario,
    problema: Problema,
    codigo_fonte: str,
    ip_address: str | None = None,
) -> SubmissaoDetalhada:
    casos = await problema_repository.list_casos_teste(db, problema.id)

    resultados_para_gravar = []
    status_geral = StatusSubmissao.ACEITO
    tempo_total_ms = 0

    for caso in casos:
        execucao = await executar(codigo_fonte, caso.entrada, problema.linguagem)
        tempo_total_ms += execucao.tempo_execucao_ms

        passou = (
            execucao.status == StatusExecucao.SUCESSO
            and execucao.stdout.strip() == caso.saida_esperada.strip()
        )
        status_caso = _status_do_caso(execucao.status, passou)
        if _PRIORIDADE_STATUS[status_caso] > _PRIORIDADE_STATUS[status_geral]:
            status_geral = status_caso

        resultados_para_gravar.append(
            {
                "caso_teste_id": caso.id,
                "passou": passou,
                "saida_obtida": execucao.stdout,
                "erro_sanitizado": execucao.erro_sanitizado,
                "tempo_execucao_ms": execucao.tempo_execucao_ms,
            }
        )

    submissao = await submissao_repository.create(
        db,
        problema_id=problema.id,
        aluno_id=aluno.id,
        codigo_fonte=codigo_fonte,
        status=status_geral,
        tempo_execucao_ms=tempo_total_ms,
    )
    resultados = await submissao_repository.create_resultados(
        db, submissao_id=submissao.id, resultados=resultados_para_gravar
    )

    await audit.registrar_evento(
        db,
        acao="submissao_criada",
        entidade="submissao",
        entidade_id=str(submissao.id),
        usuario_id=aluno.id,
        detalhes={"problema_id": str(problema.id), "status": status_geral.value},
        ip_address=ip_address,
    )

    if status_geral == StatusSubmissao.ACEITO:
        # Fecha o loop de eficacia das dicas (Parte 6): se o aluno tinha
        # dicas pendentes de resultado para este problema, esta submissao
        # aceita e o "resolveu depois da dica? em quanto tempo?".
        await dica_service.registrar_resultado_pos_dica(
            db,
            problema_id=problema.id,
            aluno_id=aluno.id,
            submissao_criado_em=submissao.criado_em,
        )

    # Gamificacao (avatar/pontuacao/emblemas): qualquer submissao conta
    # para a sequencia de dias ativos, pontos so na primeira vez que o
    # problema e resolvido. Roda na mesma transacao da submissao (nenhum
    # service aqui chama commit - ver app/core/database.py:get_db) para
    # nunca ficar dessincronizada dela.
    resultado_pontuacao = await pontuacao_service.registrar_submissao(
        db,
        aluno_id=aluno.id,
        problema_id=problema.id,
        submissao_id=submissao.id,
        nivel_dificuldade=problema.nivel_dificuldade,
        status=status_geral,
        data_atividade=submissao.criado_em.date(),
    )
    await emblema_service.avaliar_e_conceder(
        db,
        aluno_id=aluno.id,
        pontuacao=resultado_pontuacao.pontuacao,
        resolveu_problema_novo=resultado_pontuacao.resolveu_problema_novo,
        total_resolvidos=resultado_pontuacao.total_resolvidos,
    )

    return SubmissaoDetalhada(
        submissao=submissao, resultados=resultados, casos_por_id={c.id: c for c in casos}
    )


async def obter_detalhada(db: AsyncSession, submissao: Submissao) -> SubmissaoDetalhada:
    resultados = await submissao_repository.list_resultados(db, submissao.id)
    casos = await problema_repository.list_casos_teste(db, submissao.problema_id)
    return SubmissaoDetalhada(
        submissao=submissao, resultados=resultados, casos_por_id={c.id: c for c in casos}
    )
