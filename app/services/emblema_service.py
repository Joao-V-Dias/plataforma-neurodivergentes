"""Avaliacao e concessao de emblemas (conquistas): compara o estado atual
de pontuacao/progresso do aluno contra os criterios fixos definidos aqui e
concede qualquer emblema ainda nao conquistado que passou a valer.
Chamado a partir de app/services/submissao_service.py, na mesma transacao
da submissao que originou a mudanca de estado."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emblema import Emblema
from app.models.pontuacao import Pontuacao
from app.repositories import emblema_repository
from app.services import audit


@dataclass(frozen=True)
class _EstadoParaAvaliacao:
    pontuacao: Pontuacao
    total_resolvidos: int


def _primeira_solucao(estado: _EstadoParaAvaliacao) -> bool:
    return estado.total_resolvidos >= 1


def _sequencia_3_dias(estado: _EstadoParaAvaliacao) -> bool:
    return estado.pontuacao.sequencia_dias >= 3


def _sequencia_7_dias(estado: _EstadoParaAvaliacao) -> bool:
    return estado.pontuacao.sequencia_dias >= 7


def _dez_resolvidos(estado: _EstadoParaAvaliacao) -> bool:
    return estado.total_resolvidos >= 10


# Cada criterio recebe o estado ja calculado por pontuacao_service e so
# decide se foi atingido - nenhum deles faz query propria, para poder ser
# avaliado em lote sem custo extra de I/O. O codigo aqui deve bater com o
# seed de `emblemas` na migration correspondente.
_CRITERIOS: dict[str, Callable[[_EstadoParaAvaliacao], bool]] = {
    "primeira_solucao": _primeira_solucao,
    "sequencia_3_dias": _sequencia_3_dias,
    "sequencia_7_dias": _sequencia_7_dias,
    "dez_resolvidos": _dez_resolvidos,
}


async def avaliar_e_conceder(
    db: AsyncSession,
    *,
    aluno_id: uuid.UUID,
    pontuacao: Pontuacao,
    resolveu_problema_novo: bool,
    total_resolvidos: int,
) -> list[Emblema]:
    estado = _EstadoParaAvaliacao(pontuacao=pontuacao, total_resolvidos=total_resolvidos)
    ja_conquistados = await emblema_repository.get_codigos_conquistados(db, aluno_id)

    concedidos: list[Emblema] = []
    for codigo, criterio_atingido in _CRITERIOS.items():
        if codigo in ja_conquistados or not criterio_atingido(estado):
            continue
        emblema = await emblema_repository.get_por_codigo(db, codigo)
        if emblema is None:
            # Catalogo nao tem esse codigo seedado ainda - nao ha o que
            # conceder, mas nao deve quebrar o fluxo de submissao.
            continue
        await emblema_repository.conceder(db, aluno_id=aluno_id, emblema_id=emblema.id)
        await audit.registrar_evento(
            db,
            acao="emblema_concedido",
            entidade="aluno_emblema",
            entidade_id=str(emblema.id),
            usuario_id=aluno_id,
            detalhes={"codigo": emblema.codigo},
        )
        concedidos.append(emblema)

    return concedidos
