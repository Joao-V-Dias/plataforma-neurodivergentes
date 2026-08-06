"""Regras de negocio do perfil de neurodivergencia (dado sensivel de
saude - LGPD Art. 5, II; ver docs/lgpd.md secao 2). Cada chamada cria uma
nova versao; nunca alteramos uma versao existente."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.condicao_neurodivergencia import CondicaoNeurodivergencia
from app.models.perfil_aluno import PerfilAluno
from app.models.usuario import Papel, Usuario
from app.repositories import condicao_repository, perfil_aluno_repository
from app.services import audit
from app.services.exceptions import (
    AlvoInvalidoError,
    CondicaoInvalidaError,
    ConsentimentoNaoAceitoError,
    InstituicaoDiferenteError,
)


@dataclass(frozen=True)
class PerfilAlunoDetalhado:
    perfil: PerfilAluno
    condicoes: Sequence[CondicaoNeurodivergencia]


async def registrar_perfil(
    db: AsyncSession,
    *,
    aluno: Usuario,
    criado_por: Usuario,
    condicoes_codigos: Sequence[str],
    observacoes: str | None,
    aceite_consentimento: bool,
    ip_address: str | None = None,
) -> PerfilAlunoDetalhado:
    if aluno.papel != Papel.ALUNO:
        raise AlvoInvalidoError("Perfil de neurodivergencia so se aplica a usuarios Aluno.")

    if aluno.instituicao_id != criado_por.instituicao_id:
        raise InstituicaoDiferenteError("Usuario pertence a outra instituicao.")

    if not aceite_consentimento:
        raise ConsentimentoNaoAceitoError(
            "E necessario um consentimento especifico para registrar dado sensivel de saude."
        )

    condicoes = await condicao_repository.get_por_codigos(db, condicoes_codigos)
    encontrados = {c.codigo for c in condicoes}
    faltando = set(condicoes_codigos) - encontrados
    if faltando:
        raise CondicaoInvalidaError(f"Codigos de condicao invalidos: {', '.join(sorted(faltando))}")

    versao = await perfil_aluno_repository.proxima_versao(db, aluno.id)
    settings = get_settings()

    perfil = await perfil_aluno_repository.create_versao(
        db,
        aluno_id=aluno.id,
        versao=versao,
        observacoes=observacoes,
        criado_por_id=criado_por.id,
        consentimento_em=datetime.now(UTC),
        consentimento_versao=settings.lgpd_politica_versao,
        condicao_ids=[c.id for c in condicoes],
    )

    await audit.registrar_evento(
        db,
        acao="perfil_aluno_registrado",
        entidade="perfil_aluno",
        entidade_id=str(perfil.id),
        usuario_id=criado_por.id,
        detalhes={
            "aluno_id": str(aluno.id),
            "versao": versao,
            "condicoes": sorted(encontrados),
        },
        ip_address=ip_address,
    )
    return PerfilAlunoDetalhado(perfil=perfil, condicoes=condicoes)


async def obter_vigente(db: AsyncSession, aluno_id: uuid.UUID) -> PerfilAlunoDetalhado | None:
    perfil = await perfil_aluno_repository.get_vigente(db, aluno_id)
    if perfil is None:
        return None
    condicoes = await perfil_aluno_repository.get_condicoes(db, perfil.id)
    return PerfilAlunoDetalhado(perfil=perfil, condicoes=condicoes)


async def obter_historico(db: AsyncSession, aluno_id: uuid.UUID) -> list[PerfilAlunoDetalhado]:
    versoes = await perfil_aluno_repository.list_historico(db, aluno_id)
    detalhados = []
    for perfil in versoes:
        condicoes = await perfil_aluno_repository.get_condicoes(db, perfil.id)
        detalhados.append(PerfilAlunoDetalhado(perfil=perfil, condicoes=condicoes))
    return detalhados
