"""Schemas dos perfis de adaptacao: neurodivergencia, Big Five e
preferencias de acessibilidade."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CondicaoPublica(BaseModel):
    id: uuid.UUID
    codigo: str
    nome: str
    descricao: str | None

    model_config = {"from_attributes": True}


class RegistrarPerfilAlunoRequest(BaseModel):
    condicoes_codigos: list[str] = Field(
        default_factory=list,
        description="Codigos de app/GET /condicoes-neurodivergencia. Lista vazia = nenhuma "
        "condicao identificada nesta versao.",
    )
    observacoes: str | None = Field(default=None, max_length=2000)
    aceite_consentimento: bool = Field(
        ...,
        description=(
            "Consentimento explicito e especifico para tratamento deste dado sensivel de "
            "saude, distinto do consentimento geral de cadastro."
        ),
    )


class PerfilAlunoResponse(BaseModel):
    id: uuid.UUID
    aluno_id: uuid.UUID
    versao: int
    observacoes: str | None
    criado_por_id: uuid.UUID
    criado_em: datetime
    condicoes: list[CondicaoPublica]


class QuestaoTIPI(BaseModel):
    ordem: int
    texto: str


class BigFiveRespostasRequest(BaseModel):
    respostas: list[int] = Field(
        ..., min_length=10, max_length=10, description="10 respostas, escala 1 (discordo "
        "totalmente) a 7 (concordo totalmente), na ordem de GET /big-five/questionario."
    )

    @field_validator("respostas")
    @classmethod
    def _validar_escala(cls, respostas: list[int]) -> list[int]:
        if any(r < 1 or r > 7 for r in respostas):
            raise ValueError("Cada resposta deve estar entre 1 e 7.")
        return respostas


class BigFiveScores(BaseModel):
    abertura: float
    conscienciosidade: float
    extroversao: float
    amabilidade: float
    neuroticismo: float


class PerfilBigFiveResponse(BaseModel):
    id: uuid.UUID
    aluno_id: uuid.UUID
    versao: int
    criado_em: datetime
    scores: BigFiveScores
    instrumento: str


class PreferenciasAcessibilidadeRequest(BaseModel):
    fonte_legivel: bool = False
    alto_contraste: bool = False
    tempo_extra_percentual: int = Field(default=0, ge=0, le=200)
    leitura_voz_alta: bool = False
    reducao_estimulos: bool = False
    tamanho_fonte: str = Field(default="medio", pattern="^(pequeno|medio|grande|extra_grande)$")


class PreferenciasAcessibilidadeResponse(PreferenciasAcessibilidadeRequest):
    usuario_id: uuid.UUID

    model_config = {"from_attributes": True}
