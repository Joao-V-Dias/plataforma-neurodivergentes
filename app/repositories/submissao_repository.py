"""Acesso a dados de `submissoes` e `submissao_resultados`."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problema import problema_turmas
from app.models.submissao import StatusSubmissao, Submissao, SubmissaoResultado


async def create(
    db: AsyncSession,
    *,
    problema_id: uuid.UUID,
    aluno_id: uuid.UUID,
    codigo_fonte: str,
    status: StatusSubmissao,
    tempo_execucao_ms: int,
) -> Submissao:
    submissao = Submissao(
        problema_id=problema_id,
        aluno_id=aluno_id,
        codigo_fonte=codigo_fonte,
        status=status,
        tempo_execucao_ms=tempo_execucao_ms,
    )
    db.add(submissao)
    await db.flush()
    await db.refresh(submissao)
    return submissao


async def create_resultados(
    db: AsyncSession, *, submissao_id: uuid.UUID, resultados: Sequence[dict[str, Any]]
) -> list[SubmissaoResultado]:
    criados = []
    for r in resultados:
        resultado = SubmissaoResultado(
            submissao_id=submissao_id,
            caso_teste_id=r["caso_teste_id"],
            passou=r["passou"],
            saida_obtida=r["saida_obtida"],
            erro_sanitizado=r.get("erro_sanitizado"),
            tempo_execucao_ms=r["tempo_execucao_ms"],
        )
        db.add(resultado)
        criados.append(resultado)
    await db.flush()
    for resultado in criados:
        await db.refresh(resultado)
    return criados


async def get_by_id(db: AsyncSession, submissao_id: uuid.UUID) -> Submissao | None:
    return await db.get(Submissao, submissao_id)


async def list_resultados(
    db: AsyncSession, submissao_id: uuid.UUID
) -> Sequence[SubmissaoResultado]:
    result = await db.execute(
        select(SubmissaoResultado).where(SubmissaoResultado.submissao_id == submissao_id)
    )
    return result.scalars().all()


async def list_por_problema(db: AsyncSession, problema_id: uuid.UUID) -> Sequence[Submissao]:
    result = await db.execute(
        select(Submissao)
        .where(Submissao.problema_id == problema_id)
        .order_by(Submissao.criado_em.desc())
    )
    return result.scalars().all()


async def list_por_aluno_e_problema(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> Sequence[Submissao]:
    result = await db.execute(
        select(Submissao)
        .where(Submissao.problema_id == problema_id, Submissao.aluno_id == aluno_id)
        .order_by(Submissao.criado_em.desc())
    )
    return result.scalars().all()


async def contar_tentativas_na_turma(
    db: AsyncSession, *, aluno_id: uuid.UUID, turma_id: uuid.UUID
) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Submissao)
        .join(problema_turmas, problema_turmas.c.problema_id == Submissao.problema_id)
        .where(Submissao.aluno_id == aluno_id, problema_turmas.c.turma_id == turma_id)
    )
    return result.scalar_one()


async def contar_problemas_resolvidos_na_turma(
    db: AsyncSession, *, aluno_id: uuid.UUID, turma_id: uuid.UUID
) -> int:
    result = await db.execute(
        select(func.count(func.distinct(Submissao.problema_id)))
        .select_from(Submissao)
        .join(problema_turmas, problema_turmas.c.problema_id == Submissao.problema_id)
        .where(
            Submissao.aluno_id == aluno_id,
            problema_turmas.c.turma_id == turma_id,
            Submissao.status == StatusSubmissao.ACEITO,
        )
    )
    return result.scalar_one()


async def somar_tempo_execucao_na_turma(
    db: AsyncSession, *, aluno_id: uuid.UUID, turma_id: uuid.UUID
) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(Submissao.tempo_execucao_ms), 0))
        .select_from(Submissao)
        .join(problema_turmas, problema_turmas.c.problema_id == Submissao.problema_id)
        .where(Submissao.aluno_id == aluno_id, problema_turmas.c.turma_id == turma_id)
    )
    return int(result.scalar_one())
