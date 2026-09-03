"""Acesso a dados do avatar/apelido do aluno (uma linha por aluno, mutavel
in-place - mesmo padrao de preferencias_repository.py)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.avatar import PerfilJogo


async def get_by_aluno(db: AsyncSession, aluno_id: uuid.UUID) -> PerfilJogo | None:
    result = await db.execute(select(PerfilJogo).where(PerfilJogo.aluno_id == aluno_id))
    return result.scalar_one_or_none()


async def upsert(
    db: AsyncSession, *, aluno_id: uuid.UUID, apelido: str | None, avatar_codigo: str | None
) -> PerfilJogo:
    perfil = await get_by_aluno(db, aluno_id)
    if perfil is None:
        perfil = PerfilJogo(aluno_id=aluno_id)
        db.add(perfil)

    perfil.apelido = apelido
    perfil.avatar_codigo = avatar_codigo

    await db.flush()
    await db.refresh(perfil)
    return perfil
