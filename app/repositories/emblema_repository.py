"""Acesso a dados do catalogo de emblemas e das conquistas dos alunos."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emblema import Emblema, aluno_emblemas


async def list_ativos(db: AsyncSession) -> Sequence[Emblema]:
    result = await db.execute(
        select(Emblema).where(Emblema.ativo.is_(True)).order_by(Emblema.nome)
    )
    return result.scalars().all()


async def get_por_codigo(db: AsyncSession, codigo: str) -> Emblema | None:
    result = await db.execute(select(Emblema).where(Emblema.codigo == codigo))
    return result.scalar_one_or_none()


async def get_codigos_conquistados(db: AsyncSession, aluno_id: uuid.UUID) -> set[str]:
    result = await db.execute(
        select(Emblema.codigo)
        .join(aluno_emblemas, aluno_emblemas.c.emblema_id == Emblema.id)
        .where(aluno_emblemas.c.aluno_id == aluno_id)
    )
    return set(result.scalars().all())


async def conceder(db: AsyncSession, *, aluno_id: uuid.UUID, emblema_id: uuid.UUID) -> None:
    await db.execute(insert(aluno_emblemas), [{"aluno_id": aluno_id, "emblema_id": emblema_id}])
    await db.flush()


async def list_conquistados(
    db: AsyncSession, aluno_id: uuid.UUID
) -> Sequence[tuple[Emblema, datetime]]:
    result = await db.execute(
        select(Emblema, aluno_emblemas.c.conquistado_em)
        .join(aluno_emblemas, aluno_emblemas.c.emblema_id == Emblema.id)
        .where(aluno_emblemas.c.aluno_id == aluno_id)
        .order_by(aluno_emblemas.c.conquistado_em.desc())
    )
    return [(row[0], row[1]) for row in result.all()]
