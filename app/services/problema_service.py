"""Regras de negocio do banco de problemas: criacao com casos de teste e
tags, e vinculacao a turmas. A checagem "este usuario pode ver este
problema" mora em app/api/deps.py:get_problema_acessivel; aqui ficam as
regras de escrita e a montagem dos dados completos."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problema import CasoTeste, NivelDificuldade, Problema, TagProblema
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.repositories import problema_repository, tag_repository
from app.sandbox.executor import LINGUAGENS_SUPORTADAS
from app.services import audit
from app.services.exceptions import (
    InstituicaoDiferenteError,
    LinguagemNaoSuportadaError,
    TagInvalidaError,
)


@dataclass(frozen=True)
class CasoTesteInput:
    entrada: str
    saida_esperada: str
    publico: bool


@dataclass(frozen=True)
class ProblemaDetalhado:
    problema: Problema
    tags: Sequence[TagProblema]
    casos: Sequence[CasoTeste]


async def criar_problema(
    db: AsyncSession,
    *,
    criador: Usuario,
    titulo: str,
    enunciado: str,
    linguagem: str,
    nivel_dificuldade: NivelDificuldade,
    tags_codigos: Sequence[str],
    casos: Sequence[CasoTesteInput],
    ip_address: str | None = None,
) -> ProblemaDetalhado:
    if linguagem not in LINGUAGENS_SUPORTADAS:
        raise LinguagemNaoSuportadaError(
            f"Linguagem '{linguagem}' nao e suportada pelo executor. "
            f"Suportadas: {', '.join(sorted(LINGUAGENS_SUPORTADAS))}."
        )

    tags = await tag_repository.get_por_codigos(db, tags_codigos)
    encontrados = {t.codigo for t in tags}
    faltando = set(tags_codigos) - encontrados
    if faltando:
        raise TagInvalidaError(f"Codigos de tag invalidos: {', '.join(sorted(faltando))}")

    problema = await problema_repository.create(
        db,
        instituicao_id=criador.instituicao_id,
        titulo=titulo,
        enunciado=enunciado,
        linguagem=linguagem,
        nivel_dificuldade=nivel_dificuldade,
        criado_por_id=criador.id,
    )
    await problema_repository.adicionar_tags(
        db, problema_id=problema.id, tag_ids=[t.id for t in tags]
    )
    casos_criados = await problema_repository.create_casos_teste(
        db,
        problema_id=problema.id,
        casos=[
            {"entrada": c.entrada, "saida_esperada": c.saida_esperada, "publico": c.publico}
            for c in casos
        ],
    )

    await audit.registrar_evento(
        db,
        acao="problema_criado",
        entidade="problema",
        entidade_id=str(problema.id),
        usuario_id=criador.id,
        detalhes={"titulo": titulo, "linguagem": linguagem, "total_casos": len(casos_criados)},
        ip_address=ip_address,
    )
    return ProblemaDetalhado(problema=problema, tags=tags, casos=casos_criados)


async def obter_detalhe(db: AsyncSession, problema: Problema) -> ProblemaDetalhado:
    tags = await problema_repository.get_tags(db, problema.id)
    casos = await problema_repository.list_casos_teste(db, problema.id)
    return ProblemaDetalhado(problema=problema, tags=tags, casos=casos)


async def vincular_turma(
    db: AsyncSession,
    *,
    ator: Usuario,
    problema: Problema,
    turma: Turma,
    ip_address: str | None = None,
) -> None:
    if problema.instituicao_id != turma.instituicao_id:
        raise InstituicaoDiferenteError("Problema e turma pertencem a instituicoes diferentes.")

    await problema_repository.vincular_turma(db, problema_id=problema.id, turma_id=turma.id)

    await audit.registrar_evento(
        db,
        acao="problema_vinculado_turma",
        entidade="problema",
        entidade_id=str(problema.id),
        usuario_id=ator.id,
        detalhes={"turma_id": str(turma.id)},
        ip_address=ip_address,
    )


async def listar_problemas_instituicao(
    db: AsyncSession, instituicao_id: uuid.UUID
) -> Sequence[Problema]:
    return await problema_repository.list_por_instituicao(db, instituicao_id)
