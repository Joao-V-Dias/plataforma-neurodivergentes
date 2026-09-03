"""Schemas de avatar/apelido, pontuacao/sequencia de dias e emblemas."""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

AvatarCodigo = Literal[
    "raposa", "coruja", "gato", "passaro", "urso", "lobo", "tartaruga", "esquilo"
]


class PerfilJogoRequest(BaseModel):
    apelido: str | None = Field(default=None, max_length=40)
    avatar_codigo: AvatarCodigo | None = None


class PerfilJogoResponse(PerfilJogoRequest):
    aluno_id: uuid.UUID

    model_config = {"from_attributes": True}


class PontuacaoResponse(BaseModel):
    aluno_id: uuid.UUID
    pontos: int
    sequencia_dias: int
    maior_sequencia_dias: int
    ultima_atividade_em: date | None

    model_config = {"from_attributes": True}


class EmblemaResponse(BaseModel):
    id: uuid.UUID
    codigo: str
    nome: str
    descricao: str | None

    model_config = {"from_attributes": True}


class EmblemaConquistadoResponse(EmblemaResponse):
    conquistado_em: datetime
