"""Schemas do motor de dicas progressivas (Parte 6)."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class DicaResponse(BaseModel):
    id: uuid.UUID
    problema_id: uuid.UUID
    aluno_id: uuid.UUID
    nivel: int
    conteudo: str
    criado_em: datetime

    model_config = {"from_attributes": True}


class DicaComEficaciaResponse(DicaResponse):
    """Inclui o dado de eficacia - so exposto a Professor+ (ver
    app/api/v1/dicas.py), nunca ao proprio aluno, para nao pressiona-lo
    com metricas de desempenho durante o proprio aprendizado."""

    adaptacoes_aplicadas: list[str]
    resolvida_apos: bool
    tempo_ate_resolver_ms: int | None
