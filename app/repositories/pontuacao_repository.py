"""Acesso a dados de pontuacao e sequencia de dias ativos (streak) do
aluno (uma linha por aluno, mutavel in-place)."""

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pontuacao import Pontuacao


async def get_by_aluno(db: AsyncSession, aluno_id: uuid.UUID) -> Pontuacao | None:
    result = await db.execute(select(Pontuacao).where(Pontuacao.aluno_id == aluno_id))
    return result.scalar_one_or_none()


async def registrar_atividade(
    db: AsyncSession, *, aluno_id: uuid.UUID, data_atividade: date
) -> Pontuacao:
    """Atualiza a sequencia de dias ativos: continua (+1) se `data_atividade`
    e o dia seguinte ao do ultimo registro, reinicia em 1 se houve um buraco
    maior que um dia, e nao mexe em nada se ja foi contabilizada hoje -
    evita inflar a sequencia com varias submissoes no mesmo dia."""
    pontuacao = await get_by_aluno(db, aluno_id)
    if pontuacao is None:
        pontuacao = Pontuacao(
            aluno_id=aluno_id,
            sequencia_dias=1,
            maior_sequencia_dias=1,
            ultima_atividade_em=data_atividade,
        )
        db.add(pontuacao)
    elif pontuacao.ultima_atividade_em == data_atividade:
        pass
    elif pontuacao.ultima_atividade_em == data_atividade - timedelta(days=1):
        pontuacao.sequencia_dias += 1
        pontuacao.maior_sequencia_dias = max(
            pontuacao.maior_sequencia_dias, pontuacao.sequencia_dias
        )
        pontuacao.ultima_atividade_em = data_atividade
    else:
        pontuacao.sequencia_dias = 1
        pontuacao.ultima_atividade_em = data_atividade

    await db.flush()
    await db.refresh(pontuacao)
    return pontuacao


async def adicionar_pontos(db: AsyncSession, *, aluno_id: uuid.UUID, pontos: int) -> Pontuacao:
    pontuacao = await get_by_aluno(db, aluno_id)
    if pontuacao is None:
        pontuacao = Pontuacao(aluno_id=aluno_id, pontos=pontos)
        db.add(pontuacao)
    else:
        pontuacao.pontos += pontos

    await db.flush()
    await db.refresh(pontuacao)
    return pontuacao
