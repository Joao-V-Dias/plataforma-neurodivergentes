"""Progresso de aluno por turma (problemas resolvidos, tentativas, tempo
gasto), agregado a partir de `Submissao` (Parte 5): problemas_resolvidos =
numero de problemas distintos com pelo menos uma submissao aceita naquela
turma; tentativas = total de submissoes; tempo_gasto = soma do tempo de
execucao no sandbox de todas as submissoes."""

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario
from app.repositories import submissao_repository
from app.services.matricula_service import listar_matriculados


@dataclass(frozen=True)
class ProgressoAluno:
    aluno: Usuario
    problemas_resolvidos: int
    tentativas: int
    tempo_gasto_minutos: int


async def _calcular_progresso(
    db: AsyncSession, *, aluno: Usuario, turma_id: uuid.UUID
) -> ProgressoAluno:
    problemas_resolvidos = await submissao_repository.contar_problemas_resolvidos_na_turma(
        db, aluno_id=aluno.id, turma_id=turma_id
    )
    tentativas = await submissao_repository.contar_tentativas_na_turma(
        db, aluno_id=aluno.id, turma_id=turma_id
    )
    tempo_total_ms = await submissao_repository.somar_tempo_execucao_na_turma(
        db, aluno_id=aluno.id, turma_id=turma_id
    )
    return ProgressoAluno(
        aluno=aluno,
        problemas_resolvidos=problemas_resolvidos,
        tentativas=tentativas,
        tempo_gasto_minutos=tempo_total_ms // 60_000,
    )


async def obter_progresso_turma(db: AsyncSession, turma_id: uuid.UUID) -> list[ProgressoAluno]:
    matriculados = await listar_matriculados(db, turma_id)
    return [
        await _calcular_progresso(db, aluno=m.aluno, turma_id=turma_id) for m in matriculados
    ]


async def obter_progresso_aluno_na_turma(
    db: AsyncSession, *, turma_id: uuid.UUID, aluno: Usuario
) -> ProgressoAluno:
    return await _calcular_progresso(db, aluno=aluno, turma_id=turma_id)
