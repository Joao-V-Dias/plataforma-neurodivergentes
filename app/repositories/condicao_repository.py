"""Acesso a dados do vocabulario de condicoes de neurodivergencia."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.condicao_neurodivergencia import CondicaoNeurodivergencia


async def list_ativas(db: AsyncSession) -> Sequence[CondicaoNeurodivergencia]:
    result = await db.execute(
        select(CondicaoNeurodivergencia)
        .where(CondicaoNeurodivergencia.ativo.is_(True))
        .order_by(CondicaoNeurodivergencia.nome)
    )
    return result.scalars().all()


async def get_por_codigos(
    db: AsyncSession, codigos: Sequence[str]
) -> Sequence[CondicaoNeurodivergencia]:
    if not codigos:
        return []
    result = await db.execute(
        select(CondicaoNeurodivergencia).where(
            CondicaoNeurodivergencia.codigo.in_(codigos),
            CondicaoNeurodivergencia.ativo.is_(True),
        )
    )
    return result.scalars().all()


async def get_por_ids(
    db: AsyncSession, ids: Sequence[uuid.UUID]
) -> Sequence[CondicaoNeurodivergencia]:
    if not ids:
        return []
    result = await db.execute(
        select(CondicaoNeurodivergencia).where(CondicaoNeurodivergencia.id.in_(ids))
    )
    return result.scalars().all()
