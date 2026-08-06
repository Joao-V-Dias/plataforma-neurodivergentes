"""Regras de negocio de matricula/desmatricula de aluno em turma."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Papel, Usuario
from app.repositories import matricula_repository, usuario_repository
from app.services import audit
from app.services.exceptions import (
    AlvoInvalidoError,
    InstituicaoDiferenteError,
    MatriculaDuplicadaError,
    RecursoNaoEncontradoError,
)


@dataclass(frozen=True)
class MatriculaComAluno:
    matricula: Matricula
    aluno: Usuario


async def _validar_aluno(db: AsyncSession, aluno_id: uuid.UUID, turma: Turma) -> Usuario:
    aluno = await usuario_repository.get_by_id(db, aluno_id)
    if aluno is None:
        raise RecursoNaoEncontradoError("Aluno nao encontrado.")
    if aluno.papel != Papel.ALUNO:
        raise AlvoInvalidoError("Apenas usuarios com papel Aluno podem ser matriculados.")
    if aluno.instituicao_id != turma.instituicao_id:
        raise InstituicaoDiferenteError("Aluno pertence a outra instituicao.")
    return aluno


async def matricular(
    db: AsyncSession,
    *,
    ator: Usuario,
    turma: Turma,
    aluno_id: uuid.UUID,
    ip_address: str | None = None,
) -> MatriculaComAluno:
    aluno = await _validar_aluno(db, aluno_id, turma)

    if await matricula_repository.get_ativa(db, turma_id=turma.id, aluno_id=aluno_id) is not None:
        raise MatriculaDuplicadaError("Aluno ja esta matriculado nesta turma.")

    matricula = await matricula_repository.create(
        db,
        turma_id=turma.id,
        aluno_id=aluno_id,
        matriculado_por_id=ator.id,
        matriculado_em=datetime.now(UTC),
    )

    await audit.registrar_evento(
        db,
        acao="aluno_matriculado",
        entidade="matricula",
        entidade_id=str(matricula.id),
        usuario_id=ator.id,
        detalhes={"turma_id": str(turma.id), "aluno_id": str(aluno_id)},
        ip_address=ip_address,
    )
    return MatriculaComAluno(matricula=matricula, aluno=aluno)


async def desmatricular(
    db: AsyncSession,
    *,
    ator: Usuario,
    turma: Turma,
    aluno_id: uuid.UUID,
    ip_address: str | None = None,
) -> None:
    matricula = await matricula_repository.get_ativa(db, turma_id=turma.id, aluno_id=aluno_id)
    if matricula is None:
        raise RecursoNaoEncontradoError("Aluno nao tem matricula ativa nesta turma.")

    await matricula_repository.desmatricular(db, matricula, desmatriculado_em=datetime.now(UTC))

    await audit.registrar_evento(
        db,
        acao="aluno_desmatriculado",
        entidade="matricula",
        entidade_id=str(matricula.id),
        usuario_id=ator.id,
        detalhes={"turma_id": str(turma.id), "aluno_id": str(aluno_id)},
        ip_address=ip_address,
    )


async def listar_matriculados(db: AsyncSession, turma_id: uuid.UUID) -> list[MatriculaComAluno]:
    matriculas = await matricula_repository.list_ativas_por_turma(db, turma_id)
    resultado = []
    for matricula in matriculas:
        aluno = await usuario_repository.get_by_id(db, matricula.aluno_id)
        assert aluno is not None  # integridade referencial garante existencia
        resultado.append(MatriculaComAluno(matricula=matricula, aluno=aluno))
    return resultado
