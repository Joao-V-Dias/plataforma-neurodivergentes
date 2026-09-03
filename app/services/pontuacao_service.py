"""Pontuacao e sequencia de dias ativos (streak): atualizadas a partir de
cada submissao de codigo (gancho em app/services/submissao_service.py),
nunca escritas diretamente pelo cliente. Pontos so sao concedidos na
primeira vez que o aluno resolve um problema especifico - reenviar um
problema ja resolvido nao gera pontos novos, mas a sequencia de dias
continua contando qualquer submissao (reflete o espirito "pratique hoje"
de uma ofensiva, nao so "acertou hoje")."""

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problema import NivelDificuldade
from app.models.pontuacao import Pontuacao
from app.models.submissao import StatusSubmissao
from app.repositories import pontuacao_repository, submissao_repository

PONTOS_POR_DIFICULDADE: dict[NivelDificuldade, int] = {
    NivelDificuldade.FACIL: 10,
    NivelDificuldade.MEDIO: 20,
    NivelDificuldade.DIFICIL: 30,
}


@dataclass(frozen=True)
class ResultadoPontuacao:
    pontuacao: Pontuacao
    resolveu_problema_novo: bool
    total_resolvidos: int


async def registrar_submissao(
    db: AsyncSession,
    *,
    aluno_id: uuid.UUID,
    problema_id: uuid.UUID,
    submissao_id: uuid.UUID,
    nivel_dificuldade: NivelDificuldade,
    status: StatusSubmissao,
    data_atividade: date,
) -> ResultadoPontuacao:
    pontuacao = await pontuacao_repository.registrar_atividade(
        db, aluno_id=aluno_id, data_atividade=data_atividade
    )

    resolveu_problema_novo = False
    if status == StatusSubmissao.ACEITO:
        ja_resolvido = await submissao_repository.ja_resolveu_problema(
            db,
            aluno_id=aluno_id,
            problema_id=problema_id,
            excluir_submissao_id=submissao_id,
        )
        if not ja_resolvido:
            resolveu_problema_novo = True
            pontuacao = await pontuacao_repository.adicionar_pontos(
                db, aluno_id=aluno_id, pontos=PONTOS_POR_DIFICULDADE[nivel_dificuldade]
            )

    total_resolvidos = await submissao_repository.contar_problemas_resolvidos_total(db, aluno_id)

    return ResultadoPontuacao(
        pontuacao=pontuacao,
        resolveu_problema_novo=resolveu_problema_novo,
        total_resolvidos=total_resolvidos,
    )
