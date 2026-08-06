"""Acesso a dados do vocabulario de tags de problema (tema e tipo de
raciocinio - ver app/models/problema.py:TagProblema)."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problema import CategoriaTag, TagProblema


async def list_ativas(
    db: AsyncSession, categoria: CategoriaTag | None = None
) -> Sequence[TagProblema]:
    stmt = select(TagProblema).where(TagProblema.ativo.is_(True))
    if categoria is not None:
        stmt = stmt.where(TagProblema.categoria == categoria)
    result = await db.execute(stmt.order_by(TagProblema.nome))
    return result.scalars().all()


async def get_por_codigos(db: AsyncSession, codigos: Sequence[str]) -> Sequence[TagProblema]:
    if not codigos:
        return []
    result = await db.execute(
        select(TagProblema).where(TagProblema.codigo.in_(codigos), TagProblema.ativo.is_(True))
    )
    return result.scalars().all()
