"""Questionario Big Five simplificado usando o TIPI (Ten-Item Personality
Inventory):

    Gosling, S. D., Rentfrow, P. J., & Swann, W. B., Jr. (2003). A very
    brief measure of the Big Five personality domains. Journal of
    Research in Personality, 37, 504-528.

Instrumento de dominio publico, validado e amplamente citado na
literatura de psicologia da personalidade. Os 10 itens abaixo sao uma
traducao livre para PT-BR dos itens originais (nao existe traducao
oficial dos autores) - nao inventamos itens novos, apenas traduzimos os
existentes mantendo a estrutura e a escala originais.

Escala de resposta: 1 (discordo totalmente) a 7 (concordo totalmente).
Cada dimensao usa 2 itens (um direto, um reverso); o score e a media dos
dois, na escala original 1.0-7.0."""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.perfil_big_five import PerfilBigFive
from app.models.usuario import Papel, Usuario
from app.repositories import perfil_big_five_repository
from app.services import audit
from app.services.exceptions import AlvoInvalidoError

Dimensao = Literal["abertura", "conscienciosidade", "extroversao", "amabilidade", "neuroticismo"]


@dataclass(frozen=True)
class ItemTIPI:
    ordem: int
    texto: str
    dimensao: Dimensao
    reverso: bool


QUESTOES_TIPI: tuple[ItemTIPI, ...] = (
    ItemTIPI(1, "Extrovertido(a), entusiasmado(a).", "extroversao", False),
    ItemTIPI(2, "Critico(a), propenso(a) a discordar dos outros.", "amabilidade", True),
    ItemTIPI(3, "Confiavel, autodisciplinado(a).", "conscienciosidade", False),
    ItemTIPI(4, "Ansioso(a), facilmente perturbavel.", "neuroticismo", False),
    ItemTIPI(5, "Aberto(a) a novas experiencias, complexo(a).", "abertura", False),
    ItemTIPI(6, "Reservado(a), quieto(a).", "extroversao", True),
    ItemTIPI(7, "Solidario(a), caloroso(a).", "amabilidade", False),
    ItemTIPI(8, "Desorganizado(a), descuidado(a).", "conscienciosidade", True),
    ItemTIPI(9, "Calmo(a), emocionalmente estavel.", "neuroticismo", True),
    ItemTIPI(10, "Convencional, pouco criativo(a).", "abertura", True),
)

INSTRUMENTO_REF = (
    "TIPI - Ten-Item Personality Inventory (Gosling, Rentfrow & Swann, 2003), "
    "traducao livre PT-BR"
)


def _valor(resposta: int, *, reverso: bool) -> float:
    return float(8 - resposta) if reverso else float(resposta)


def calcular_scores(respostas: list[int]) -> dict[str, float]:
    if len(respostas) != 10:
        raise ValueError("Sao esperadas exatamente 10 respostas (uma por item do TIPI).")
    if any(r < 1 or r > 7 for r in respostas):
        raise ValueError("Cada resposta deve estar entre 1 e 7.")

    somas: dict[Dimensao, list[float]] = {
        "abertura": [],
        "conscienciosidade": [],
        "extroversao": [],
        "amabilidade": [],
        "neuroticismo": [],
    }
    for item, resposta in zip(QUESTOES_TIPI, respostas, strict=True):
        somas[item.dimensao].append(_valor(resposta, reverso=item.reverso))

    return {dimensao: sum(valores) / len(valores) for dimensao, valores in somas.items()}


async def registrar_respostas(
    db: AsyncSession,
    *,
    aluno: Usuario,
    respostas: list[int],
    ip_address: str | None = None,
) -> PerfilBigFive:
    if aluno.papel != Papel.ALUNO:
        raise AlvoInvalidoError("O questionario Big Five e um autorrelato, exclusivo de Aluno.")

    scores = calcular_scores(respostas)
    versao = await perfil_big_five_repository.proxima_versao(db, aluno.id)

    perfil = await perfil_big_five_repository.create_versao(
        db,
        aluno_id=aluno.id,
        versao=versao,
        scores=scores,
        respostas_brutas=respostas,
    )

    await audit.registrar_evento(
        db,
        acao="perfil_big_five_registrado",
        entidade="perfil_big_five",
        entidade_id=str(perfil.id),
        usuario_id=aluno.id,
        detalhes={"versao": versao, "instrumento": INSTRUMENTO_REF},
        ip_address=ip_address,
    )
    return perfil
