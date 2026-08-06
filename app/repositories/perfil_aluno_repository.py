"""Acesso a dados do perfil de neurodivergencia do aluno (versionado,
append-only - ver app/models/perfil_aluno.py)."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.condicao_neurodivergencia import CondicaoNeurodivergencia
from app.models.perfil_aluno import PerfilAluno, perfil_aluno_condicoes


async def get_vigente(db: AsyncSession, aluno_id: uuid.UUID) -> PerfilAluno | None:
    result = await db.execute(
        select(PerfilAluno)
        .where(PerfilAluno.aluno_id == aluno_id)
        .order_by(PerfilAluno.versao.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_historico(db: AsyncSession, aluno_id: uuid.UUID) -> Sequence[PerfilAluno]:
    result = await db.execute(
        select(PerfilAluno)
        .where(PerfilAluno.aluno_id == aluno_id)
        .order_by(PerfilAluno.versao.desc())
    )
    return result.scalars().all()


async def proxima_versao(db: AsyncSession, aluno_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.max(PerfilAluno.versao)).where(PerfilAluno.aluno_id == aluno_id)
    )
    maior_versao = result.scalar_one_or_none()
    return (maior_versao or 0) + 1


async def get_condicoes(
    db: AsyncSession, perfil_aluno_id: uuid.UUID
) -> Sequence[CondicaoNeurodivergencia]:
    result = await db.execute(
        select(CondicaoNeurodivergencia)
        .join(
            perfil_aluno_condicoes,
            perfil_aluno_condicoes.c.condicao_id == CondicaoNeurodivergencia.id,
        )
        .where(perfil_aluno_condicoes.c.perfil_aluno_id == perfil_aluno_id)
        .order_by(CondicaoNeurodivergencia.nome)
    )
    return result.scalars().all()


async def create_versao(
    db: AsyncSession,
    *,
    aluno_id: uuid.UUID,
    versao: int,
    observacoes: str | None,
    criado_por_id: uuid.UUID,
    consentimento_em: datetime,
    consentimento_versao: str,
    condicao_ids: Sequence[uuid.UUID],
) -> PerfilAluno:
    perfil = PerfilAluno(
        aluno_id=aluno_id,
        versao=versao,
        observacoes=observacoes,
        criado_por_id=criado_por_id,
        consentimento_em=consentimento_em,
        consentimento_versao=consentimento_versao,
    )
    db.add(perfil)
    await db.flush()
    await db.refresh(perfil)

    if condicao_ids:
        await db.execute(
            insert(perfil_aluno_condicoes),
            [{"perfil_aluno_id": perfil.id, "condicao_id": cid} for cid in condicao_ids],
        )
        await db.flush()

    return perfil
