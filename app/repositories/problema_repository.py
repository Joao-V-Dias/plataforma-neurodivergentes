"""Acesso a dados de `problemas`, `casos_teste`, `problema_tags` e
`problema_turmas`."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.matricula import Matricula
from app.models.problema import (
    CasoTeste,
    NivelDificuldade,
    Problema,
    TagProblema,
    problema_tags,
    problema_turmas,
)


async def get_by_id(db: AsyncSession, problema_id: uuid.UUID) -> Problema | None:
    return await db.get(Problema, problema_id)


async def list_por_instituicao(db: AsyncSession, instituicao_id: uuid.UUID) -> Sequence[Problema]:
    result = await db.execute(
        select(Problema)
        .where(Problema.instituicao_id == instituicao_id, Problema.ativo.is_(True))
        .order_by(Problema.titulo)
    )
    return result.scalars().all()


async def list_por_turma(db: AsyncSession, turma_id: uuid.UUID) -> Sequence[Problema]:
    result = await db.execute(
        select(Problema)
        .join(problema_turmas, problema_turmas.c.problema_id == Problema.id)
        .where(problema_turmas.c.turma_id == turma_id, Problema.ativo.is_(True))
        .order_by(Problema.titulo)
    )
    return result.scalars().all()


async def create(
    db: AsyncSession,
    *,
    instituicao_id: uuid.UUID,
    titulo: str,
    enunciado: str,
    linguagem: str,
    nivel_dificuldade: NivelDificuldade,
    criado_por_id: uuid.UUID,
) -> Problema:
    problema = Problema(
        instituicao_id=instituicao_id,
        titulo=titulo,
        enunciado=enunciado,
        linguagem=linguagem,
        nivel_dificuldade=nivel_dificuldade,
        criado_por_id=criado_por_id,
    )
    db.add(problema)
    await db.flush()
    await db.refresh(problema)
    return problema


async def adicionar_tags(
    db: AsyncSession, *, problema_id: uuid.UUID, tag_ids: Sequence[uuid.UUID]
) -> None:
    if not tag_ids:
        return
    await db.execute(
        insert(problema_tags), [{"problema_id": problema_id, "tag_id": tid} for tid in tag_ids]
    )
    await db.flush()


async def get_tags(db: AsyncSession, problema_id: uuid.UUID) -> Sequence[TagProblema]:
    result = await db.execute(
        select(TagProblema)
        .join(problema_tags, problema_tags.c.tag_id == TagProblema.id)
        .where(problema_tags.c.problema_id == problema_id)
        .order_by(TagProblema.categoria, TagProblema.nome)
    )
    return result.scalars().all()


async def vincular_turma(db: AsyncSession, *, problema_id: uuid.UUID, turma_id: uuid.UUID) -> None:
    if await turma_vinculada(db, problema_id, turma_id):
        return
    await db.execute(insert(problema_turmas), [{"problema_id": problema_id, "turma_id": turma_id}])
    await db.flush()


async def turma_vinculada(db: AsyncSession, problema_id: uuid.UUID, turma_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(problema_turmas.c.problema_id).where(
            problema_turmas.c.problema_id == problema_id,
            problema_turmas.c.turma_id == turma_id,
        )
    )
    return result.first() is not None


async def aluno_tem_acesso(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> bool:
    """Aluno so acessa um problema se ele estiver vinculado a uma turma em
    que o aluno tem matricula ativa - ver Parte 4."""
    result = await db.execute(
        select(problema_turmas.c.problema_id)
        .join(Matricula, Matricula.turma_id == problema_turmas.c.turma_id)
        .where(
            problema_turmas.c.problema_id == problema_id,
            Matricula.aluno_id == aluno_id,
            Matricula.ativo.is_(True),
        )
        .limit(1)
    )
    return result.first() is not None


async def create_casos_teste(
    db: AsyncSession,
    *,
    problema_id: uuid.UUID,
    casos: Sequence[dict[str, Any]],
) -> list[CasoTeste]:
    criados = []
    for i, caso in enumerate(casos):
        caso_teste = CasoTeste(
            problema_id=problema_id,
            entrada=caso["entrada"],
            saida_esperada=caso["saida_esperada"],
            publico=caso["publico"],
            ordem=i,
        )
        db.add(caso_teste)
        criados.append(caso_teste)
    await db.flush()
    for caso_teste in criados:
        await db.refresh(caso_teste)
    return criados


async def list_casos_teste(db: AsyncSession, problema_id: uuid.UUID) -> Sequence[CasoTeste]:
    result = await db.execute(
        select(CasoTeste).where(CasoTeste.problema_id == problema_id).order_by(CasoTeste.ordem)
    )
    return result.scalars().all()


async def get_caso_teste(db: AsyncSession, caso_teste_id: uuid.UUID) -> CasoTeste | None:
    return await db.get(CasoTeste, caso_teste_id)
