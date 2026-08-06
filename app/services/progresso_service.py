"""Progresso de aluno por turma (problemas resolvidos, tentativas, tempo
gasto). O endpoint e entregue ja na Parte 4 porque a estrutura de
visibilidade (quem pode ver o progresso de quem) e parte da gestao
academica - mas os NUMEROS ainda sao placeholder (zero), porque o modelo
de submissao (`Submissao`/`Problema`) so existe a partir da Parte 5.

Quando a Parte 5 existir, troque o corpo de `_progresso_zerado` por uma
consulta real de agregacao sobre a tabela de submissoes, filtrando por
aluno_id + turma_id (via problemas vinculados aquela turma)."""

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario
from app.services.matricula_service import listar_matriculados


@dataclass(frozen=True)
class ProgressoAluno:
    aluno: Usuario
    problemas_resolvidos: int
    tentativas: int
    tempo_gasto_minutos: int


def _progresso_zerado(aluno: Usuario) -> ProgressoAluno:
    return ProgressoAluno(
        aluno=aluno, problemas_resolvidos=0, tentativas=0, tempo_gasto_minutos=0
    )


async def obter_progresso_turma(db: AsyncSession, turma_id: uuid.UUID) -> list[ProgressoAluno]:
    matriculados = await listar_matriculados(db, turma_id)
    return [_progresso_zerado(m.aluno) for m in matriculados]


async def obter_progresso_aluno_na_turma(
    db: AsyncSession, *, turma_id: uuid.UUID, aluno: Usuario
) -> ProgressoAluno:
    return _progresso_zerado(aluno)
