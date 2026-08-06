"""Regras de negocio de Turma: criacao, co-docencia e visibilidade por
papel (Professor so ve suas turmas vinculadas; Coordenador/Diretor veem
toda a instituicao - a checagem de acesso a uma turma especifica mora em
app/api/deps.py:get_turma_acessivel; aqui ficam as regras de escrita e a
listagem)."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.turma import Turma
from app.models.usuario import Papel, Usuario
from app.repositories import matricula_repository, turma_repository, usuario_repository
from app.services import audit
from app.services.exceptions import (
    AlvoInvalidoError,
    InstituicaoDiferenteError,
    RecursoNaoEncontradoError,
)


@dataclass(frozen=True)
class TurmaDetalhada:
    turma: Turma
    total_professores: int
    total_alunos_ativos: int


async def _validar_professor(
    db: AsyncSession, professor_id: uuid.UUID, instituicao_id: uuid.UUID
) -> None:
    professor = await usuario_repository.get_by_id(db, professor_id)
    if professor is None:
        raise RecursoNaoEncontradoError("Professor nao encontrado.")
    if professor.papel != Papel.PROFESSOR:
        raise AlvoInvalidoError("O usuario indicado nao tem papel de Professor.")
    if professor.instituicao_id != instituicao_id:
        raise InstituicaoDiferenteError("Professor pertence a outra instituicao.")


async def criar_turma(
    db: AsyncSession,
    *,
    criador: Usuario,
    nome: str,
    periodo: str,
    professor_responsavel_id: uuid.UUID,
    ip_address: str | None = None,
) -> Turma:
    await _validar_professor(db, professor_responsavel_id, criador.instituicao_id)

    turma = await turma_repository.create(
        db,
        instituicao_id=criador.instituicao_id,
        nome=nome,
        periodo=periodo,
        professor_responsavel_id=professor_responsavel_id,
    )

    await audit.registrar_evento(
        db,
        acao="turma_criada",
        entidade="turma",
        entidade_id=str(turma.id),
        usuario_id=criador.id,
        detalhes={"nome": nome, "periodo": periodo},
        ip_address=ip_address,
    )
    return turma


async def adicionar_professor(
    db: AsyncSession,
    *,
    ator: Usuario,
    turma: Turma,
    professor_id: uuid.UUID,
    ip_address: str | None = None,
) -> None:
    await _validar_professor(db, professor_id, turma.instituicao_id)
    await turma_repository.adicionar_professor(db, turma_id=turma.id, professor_id=professor_id)

    await audit.registrar_evento(
        db,
        acao="turma_professor_adicionado",
        entidade="turma",
        entidade_id=str(turma.id),
        usuario_id=ator.id,
        detalhes={"professor_id": str(professor_id)},
        ip_address=ip_address,
    )


async def listar_turmas_visiveis(db: AsyncSession, usuario: Usuario) -> Sequence[Turma]:
    if usuario.papel == Papel.PROFESSOR:
        return await turma_repository.list_por_professor(db, usuario.id)
    return await turma_repository.list_por_instituicao(db, usuario.instituicao_id)


async def obter_detalhe(db: AsyncSession, turma: Turma) -> TurmaDetalhada:
    total_professores = await turma_repository.contar_professores(db, turma.id)
    total_alunos_ativos = await matricula_repository.contar_ativas(db, turma.id)
    return TurmaDetalhada(
        turma=turma,
        total_professores=total_professores,
        total_alunos_ativos=total_alunos_ativos,
    )
