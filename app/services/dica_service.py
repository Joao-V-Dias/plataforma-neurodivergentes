"""Orquestra o motor de dicas progressivas (Parte 6): calcula o proximo
nivel para o aluno+problema, monta o contexto de perfil (condicoes de
neurodivergencia + Big Five, ver PerfilAluno/PerfilBigFive da Parte 3),
aciona o motor de IA isolado em app/ai e persiste + audita o resultado.

Guardrail estrutural de progressao: o aluno nunca escolhe o nivel da dica
via API - este service sempre calcula nivel_maximo_ja_dado + 1. Isso torna
impossivel pular uma etapa mesmo que o cliente tente forcar um nivel
especifico, porque o endpoint nem aceita esse parametro (ver
app/api/v1/dicas.py)."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import prompts
from app.ai.groq_client import gerar_texto
from app.core.config import get_settings
from app.models.dica import Dica
from app.models.problema import CategoriaTag, Problema
from app.models.usuario import Usuario
from app.repositories import (
    dica_repository,
    perfil_aluno_repository,
    perfil_big_five_repository,
    problema_repository,
    submissao_repository,
)
from app.services import audit
from app.services.exceptions import NivelMaximoDeDicasAtingidoError

# Codigo fonte da ultima tentativa e enviado ao provedor externo como
# contexto - limitamos o tamanho para nao mandar submissoes gigantes sem
# necessidade (o modelo so precisa de contexto suficiente para entender o
# que o aluno ja tentou).
_MAX_CHARS_ULTIMA_TENTATIVA = 4_000


@dataclass(frozen=True)
class DicaGerada:
    dica: Dica
    nivel_maximo: int


async def _montar_contexto_problema(
    db: AsyncSession, problema: Problema
) -> prompts.ContextoProblema:
    tags = await problema_repository.get_tags(db, problema.id)
    tags_raciocinio = [t.nome for t in tags if t.categoria == CategoriaTag.RACIOCINIO]
    return prompts.ContextoProblema(
        titulo=problema.titulo,
        enunciado=problema.enunciado,
        linguagem=problema.linguagem,
        tags_raciocinio=tags_raciocinio,
    )


async def _montar_contexto_aluno(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> prompts.ContextoAluno:
    condicoes: list[str] = []
    perfil = await perfil_aluno_repository.get_vigente(db, aluno_id)
    if perfil is not None:
        condicoes_obj = await perfil_aluno_repository.get_condicoes(db, perfil.id)
        condicoes = [c.codigo for c in condicoes_obj]

    big_five = None
    perfil_bf = await perfil_big_five_repository.get_vigente(db, aluno_id)
    if perfil_bf is not None:
        big_five = {
            "abertura": perfil_bf.score_abertura,
            "conscienciosidade": perfil_bf.score_conscienciosidade,
            "extroversao": perfil_bf.score_extroversao,
            "amabilidade": perfil_bf.score_amabilidade,
            "neuroticismo": perfil_bf.score_neuroticismo,
        }

    ultima_tentativa = None
    submissoes = await submissao_repository.list_por_aluno_e_problema(
        db, problema_id=problema_id, aluno_id=aluno_id
    )
    if submissoes:
        ultima_tentativa = submissoes[0].codigo_fonte[:_MAX_CHARS_ULTIMA_TENTATIVA]

    return prompts.ContextoAluno(
        condicoes=condicoes, big_five=big_five, ultima_tentativa_codigo=ultima_tentativa
    )


async def solicitar_proxima_dica(
    db: AsyncSession, *, aluno: Usuario, problema: Problema, ip_address: str | None = None
) -> DicaGerada:
    settings = get_settings()
    nivel_atual = await dica_repository.get_nivel_maximo(
        db, problema_id=problema.id, aluno_id=aluno.id
    )
    if nivel_atual >= settings.dica_niveis_maximo:
        raise NivelMaximoDeDicasAtingidoError(
            "Voce ja recebeu a dica de nivel mais alto disponivel para este problema."
        )
    proximo_nivel = nivel_atual + 1

    contexto_problema = await _montar_contexto_problema(db, problema)
    contexto_aluno = await _montar_contexto_aluno(
        db, problema_id=problema.id, aluno_id=aluno.id
    )

    prompt = prompts.montar_prompt(
        nivel=proximo_nivel, problema=contexto_problema, aluno=contexto_aluno
    )
    conteudo = await gerar_texto(
        system_prompt=prompt.system_prompt, mensagem_usuario=prompt.mensagem_usuario
    )

    dica = await dica_repository.create(
        db,
        problema_id=problema.id,
        aluno_id=aluno.id,
        nivel=proximo_nivel,
        conteudo=conteudo,
        adaptacoes_aplicadas=prompt.adaptacoes_aplicadas,
    )

    await audit.registrar_evento(
        db,
        acao="dica_gerada",
        entidade="dica",
        entidade_id=str(dica.id),
        usuario_id=aluno.id,
        detalhes={
            "problema_id": str(problema.id),
            "nivel": proximo_nivel,
            "adaptacoes_aplicadas": prompt.adaptacoes_aplicadas,
        },
        ip_address=ip_address,
    )

    return DicaGerada(dica=dica, nivel_maximo=proximo_nivel)


async def listar_historico(
    db: AsyncSession, *, problema_id: uuid.UUID, aluno_id: uuid.UUID
) -> Sequence[Dica]:
    return await dica_repository.list_por_aluno_e_problema(
        db, problema_id=problema_id, aluno_id=aluno_id
    )


async def registrar_resultado_pos_dica(
    db: AsyncSession,
    *,
    problema_id: uuid.UUID,
    aluno_id: uuid.UUID,
    submissao_criado_em: datetime,
) -> None:
    """Chamado por app/services/submissao_service.py quando uma submissao
    e aceita: marca toda dica ainda sem resultado para este aluno+problema
    como "resolvida apos a dica", com o tempo decorrido entre a dica e a
    submissao aceita. E o dado de eficacia usado para calibrar o sistema
    ao longo do tempo (criterio de aceite da Parte 6)."""
    pendentes = await dica_repository.list_pendentes_de_resultado(
        db, problema_id=problema_id, aluno_id=aluno_id
    )
    for dica in pendentes:
        delta_ms = int((submissao_criado_em - dica.criado_em).total_seconds() * 1000)
        await dica_repository.marcar_resolvida(
            db, dica=dica, tempo_ate_resolver_ms=max(delta_ms, 0)
        )
