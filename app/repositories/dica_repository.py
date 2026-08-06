"""Acesso a dados de `dicas` (Parte 6)."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dica import Dica


async def get_nivel_maximo(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> int:
    """Maior nivel de dica ja entregue a este aluno para este problema, ou
    0 se nenhuma dica foi pedida ainda. E a base para calcular o proximo
    nivel a gerar - o aluno nunca escolhe o nivel (ver
    app/services/dica_service.py)."""
    result = await db.execute(
        select(func.max(Dica.nivel)).where(
            Dica.problema_id == problema_id, Dica.aluno_id == aluno_id
        )
    )
    return result.scalar_one_or_none() or 0


async def list_por_aluno_e_problema(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> Sequence[Dica]:
    result = await db.execute(
        select(Dica)
        .where(Dica.problema_id == problema_id, Dica.aluno_id == aluno_id)
        .order_by(Dica.nivel)
    )
    return result.scalars().all()


async def list_pendentes_de_resultado(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> Sequence[Dica]:
    """Dicas ja entregues para este aluno+problema que ainda nao foram
    associadas a uma submissao aceita - usado para calcular a eficacia
    quando uma submissao aceita chega (ver
    app/services/dica_service.registrar_resultado_pos_dica)."""
    result = await db.execute(
        select(Dica).where(
            Dica.problema_id == problema_id,
            Dica.aluno_id == aluno_id,
            Dica.resolvida_apos.is_(False),
        )
    )
    return result.scalars().all()


async def create(
    db: AsyncSession,
    *,
    problema_id: uuid.UUID,
    aluno_id: uuid.UUID,
    nivel: int,
    conteudo: str,
    adaptacoes_aplicadas: Sequence[str],
) -> Dica:
    dica = Dica(
        problema_id=problema_id,
        aluno_id=aluno_id,
        nivel=nivel,
        conteudo=conteudo,
        adaptacoes_aplicadas=list(adaptacoes_aplicadas),
    )
    db.add(dica)
    await db.flush()
    await db.refresh(dica)
    return dica


async def marcar_resolvida(db: AsyncSession, *, dica: Dica, tempo_ate_resolver_ms: int) -> None:
    dica.resolvida_apos = True
    dica.tempo_ate_resolver_ms = tempo_ate_resolver_ms
    db.add(dica)
    await db.flush()
