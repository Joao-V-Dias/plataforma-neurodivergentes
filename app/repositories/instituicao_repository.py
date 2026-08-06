"""Acesso a dados da tabela `instituicoes`."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instituicao import Instituicao


async def get_by_id(db: AsyncSession, instituicao_id: uuid.UUID) -> Instituicao | None:
    return await db.get(Instituicao, instituicao_id)


async def get_by_codigo(db: AsyncSession, codigo: str) -> Instituicao | None:
    result = await db.execute(
        select(Instituicao).where(Instituicao.codigo == codigo.upper(), Instituicao.ativo.is_(True))
    )
    return result.scalar_one_or_none()
