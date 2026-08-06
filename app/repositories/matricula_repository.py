"""Acesso a dados de `matriculas`."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.matricula import Matricula


async def get_ativa(
    db: AsyncSession, *, turma_id: uuid.UUID, aluno_id: uuid.UUID
) -> Matricula | None:
    result = await db.execute(
        select(Matricula).where(
            Matricula.turma_id == turma_id,
            Matricula.aluno_id == aluno_id,
            Matricula.ativo.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def list_ativas_por_turma(db: AsyncSession, turma_id: uuid.UUID) -> Sequence[Matricula]:
    result = await db.execute(
        select(Matricula)
        .where(Matricula.turma_id == turma_id, Matricula.ativo.is_(True))
        .order_by(Matricula.matriculado_em)
    )
    return result.scalars().all()


async def list_ativas_por_aluno(db: AsyncSession, aluno_id: uuid.UUID) -> Sequence[Matricula]:
    result = await db.execute(
        select(Matricula)
        .where(Matricula.aluno_id == aluno_id, Matricula.ativo.is_(True))
        .order_by(Matricula.matriculado_em)
    )
    return result.scalars().all()


async def contar_ativas(db: AsyncSession, turma_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Matricula)
        .where(Matricula.turma_id == turma_id, Matricula.ativo.is_(True))
    )
    return result.scalar_one()


async def create(
    db: AsyncSession,
    *,
    turma_id: uuid.UUID,
    aluno_id: uuid.UUID,
    matriculado_por_id: uuid.UUID,
    matriculado_em: datetime,
) -> Matricula:
    matricula = Matricula(
        turma_id=turma_id,
        aluno_id=aluno_id,
        matriculado_por_id=matriculado_por_id,
        matriculado_em=matriculado_em,
        ativo=True,
    )
    db.add(matricula)
    await db.flush()
    await db.refresh(matricula)
    return matricula


async def desmatricular(
    db: AsyncSession, matricula: Matricula, *, desmatriculado_em: datetime
) -> None:
    matricula.ativo = False
    matricula.desmatriculado_em = desmatriculado_em
    db.add(matricula)
    await db.flush()
