"""Acesso a dados de `turmas` e `turma_professores`."""

import uuid
from collections.abc import Sequence

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.turma import Turma, turma_professores


async def get_by_id(db: AsyncSession, turma_id: uuid.UUID) -> Turma | None:
    return await db.get(Turma, turma_id)


async def list_por_instituicao(db: AsyncSession, instituicao_id: uuid.UUID) -> Sequence[Turma]:
    result = await db.execute(
        select(Turma).where(Turma.instituicao_id == instituicao_id).order_by(Turma.nome)
    )
    return result.scalars().all()


async def list_por_professor(db: AsyncSession, professor_id: uuid.UUID) -> Sequence[Turma]:
    result = await db.execute(
        select(Turma)
        .join(turma_professores, turma_professores.c.turma_id == Turma.id)
        .where(turma_professores.c.professor_id == professor_id)
        .order_by(Turma.nome)
    )
    return result.scalars().all()


async def professor_vinculado(
    db: AsyncSession, turma_id: uuid.UUID, professor_id: uuid.UUID
) -> bool:
    result = await db.execute(
        select(turma_professores.c.turma_id).where(
            turma_professores.c.turma_id == turma_id,
            turma_professores.c.professor_id == professor_id,
        )
    )
    return result.first() is not None


async def create(
    db: AsyncSession,
    *,
    instituicao_id: uuid.UUID,
    nome: str,
    periodo: str,
    professor_responsavel_id: uuid.UUID,
) -> Turma:
    turma = Turma(
        instituicao_id=instituicao_id,
        nome=nome,
        periodo=periodo,
        professor_responsavel_id=professor_responsavel_id,
    )
    db.add(turma)
    await db.flush()
    await db.refresh(turma)

    await db.execute(
        insert(turma_professores),
        [{"turma_id": turma.id, "professor_id": professor_responsavel_id}],
    )
    await db.flush()
    return turma


async def adicionar_professor(
    db: AsyncSession, *, turma_id: uuid.UUID, professor_id: uuid.UUID
) -> None:
    if await professor_vinculado(db, turma_id, professor_id):
        return
    await db.execute(
        insert(turma_professores), [{"turma_id": turma_id, "professor_id": professor_id}]
    )
    await db.flush()


async def list_professores(db: AsyncSession, turma_id: uuid.UUID) -> Sequence[uuid.UUID]:
    result = await db.execute(
        select(turma_professores.c.professor_id).where(turma_professores.c.turma_id == turma_id)
    )
    return result.scalars().all()


async def contar_professores(db: AsyncSession, turma_id: uuid.UUID) -> int:
    professores = await list_professores(db, turma_id)
    return len(professores)
