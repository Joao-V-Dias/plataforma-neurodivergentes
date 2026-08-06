"""Acesso a dados do perfil Big Five (versionado, append-only)."""

import uuid
from collections.abc import Mapping, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.perfil_big_five import PerfilBigFive


async def get_vigente(db: AsyncSession, aluno_id: uuid.UUID) -> PerfilBigFive | None:
    result = await db.execute(
        select(PerfilBigFive)
        .where(PerfilBigFive.aluno_id == aluno_id)
        .order_by(PerfilBigFive.versao.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_historico(db: AsyncSession, aluno_id: uuid.UUID) -> Sequence[PerfilBigFive]:
    result = await db.execute(
        select(PerfilBigFive)
        .where(PerfilBigFive.aluno_id == aluno_id)
        .order_by(PerfilBigFive.versao.desc())
    )
    return result.scalars().all()


async def proxima_versao(db: AsyncSession, aluno_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.max(PerfilBigFive.versao)).where(PerfilBigFive.aluno_id == aluno_id)
    )
    maior_versao = result.scalar_one_or_none()
    return (maior_versao or 0) + 1


async def create_versao(
    db: AsyncSession,
    *,
    aluno_id: uuid.UUID,
    versao: int,
    scores: Mapping[str, float],
    respostas_brutas: list[int],
) -> PerfilBigFive:
    perfil = PerfilBigFive(
        aluno_id=aluno_id,
        versao=versao,
        score_abertura=scores["abertura"],
        score_conscienciosidade=scores["conscienciosidade"],
        score_extroversao=scores["extroversao"],
        score_amabilidade=scores["amabilidade"],
        score_neuroticismo=scores["neuroticismo"],
        respostas_brutas=respostas_brutas,
    )
    db.add(perfil)
    await db.flush()
    await db.refresh(perfil)
    return perfil
